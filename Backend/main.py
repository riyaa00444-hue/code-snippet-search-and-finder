import os
import ast
import sqlite3
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# -------------------- ENV --------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
VECTOR_DIR = os.path.join(BASE_DIR, "vector_store")

os.makedirs(VECTOR_DIR, exist_ok=True)

# -------------------- APP --------------------
app = FastAPI(title="Code Snippet Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE --------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        path TEXT,
        description TEXT,
        file_list TEXT,
        file_count INTEGER,
        indexed INTEGER DEFAULT 0,
        analyzed_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS code_snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repository_id INTEGER,
        file_path TEXT,
        code TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        result_count INTEGER,
        searched_at TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# -------------------- SCHEMAS --------------------
class AddRepositoryRequest(BaseModel):
    name: str
    path: str


# -------------------- HELPERS --------------------
def analyze_repository(repo_path: str):
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")

    files = []
    for root, _, filenames in os.walk(repo_path):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), repo_path))

    description = "Repository analysis not available"
    if GOOGLE_API_KEY:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=GOOGLE_API_KEY,
        )
        prompt = f"Explain briefly what this repository does:\n{files[:30]}"
        description = llm.invoke(prompt).content

    return description, files


def parse_python_file(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    tree = ast.parse(source)
    snippets = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            snippets.append(ast.get_source_segment(source, node))

    return snippets


# -------------------- REPOSITORIES --------------------
@app.post("/api/repositories")
def add_repository(repo: AddRepositoryRequest):
    desc, files = analyze_repository(repo.path)

    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
    INSERT INTO repositories
    (name, path, description, file_list, file_count, analyzed_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (repo.name, repo.path, desc, ",".join(files), len(files), now))

    conn.commit()
    conn.close()

    return {"name": repo.name, "description": desc, "files": files}


@app.get("/api/repositories")
def list_repositories():
    conn = get_db()
    rows = conn.execute("SELECT * FROM repositories").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/repositories/{repo_id}")
def get_repository_detail(repo_id: int):
    conn = get_db()
    repo = conn.execute(
        "SELECT * FROM repositories WHERE id = ?", (repo_id,)
    ).fetchone()
    conn.close()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    files = repo["file_list"].split(",") if repo["file_list"] else []

    return {
        "id": repo["id"],
        "name": repo["name"],
        "path": repo["path"],
        "description": repo["description"],
        "files": files,
        "file_count": repo["file_count"],
        "indexed": repo["indexed"],
        "analyzed_at": repo["analyzed_at"],
    }


# -------------------- INDEXING --------------------
@app.post("/api/repositories/{repo_id}/index")
def index_repository(repo_id: int):
    conn = get_db()
    repo = conn.execute(
        "SELECT * FROM repositories WHERE id = ?", (repo_id,)
    ).fetchone()

    if not repo:
        raise HTTPException(404, "Repository not found")

    snippets = []
    for root, _, files in os.walk(repo["path"]):
        if "node_modules" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                snippets += parse_python_file(os.path.join(root, f))

    if not snippets:
        raise HTTPException(400, "No Python code found")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    metadatas = []
    for code in snippets:
        cur = conn.execute("""
        INSERT INTO code_snippets (repository_id, file_path, code)
        VALUES (?, ?, ?)
        """, (repo_id, repo["path"], code))
        metadatas.append({"snippet_id": cur.lastrowid, "repository_id": repo_id})

    vector_store = FAISS.from_texts(snippets, embeddings, metadatas=metadatas)
    vector_store.save_local(VECTOR_DIR)

    conn.execute(
        "UPDATE repositories SET indexed = 1 WHERE id = ?", (repo_id,)
    )
    conn.commit()
    conn.close()

    return {"status": "indexed", "snippets": len(snippets)}


# -------------------- ISSUE 12: SEARCH --------------------
def save_search_history(query: str, count: int):
    conn = get_db()
    conn.execute("""
    INSERT INTO search_history (query, result_count, searched_at)
    VALUES (?, ?, ?)
    """, (query, count, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


@app.get("/api/search")
def search_code(
    query: str = Query(..., min_length=3),
    repoId: Optional[int] = Query(None),
):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        VECTOR_DIR, embeddings, allow_dangerous_deserialization=True
    )

    results = vector_store.similarity_search_with_score(query, k=5)

    conn = get_db()
    matches = []

    for doc, score in results:
        if repoId and doc.metadata.get("repository_id") != repoId:
            continue

        row = conn.execute("""
        SELECT id, repository_id, file_path, code
        FROM code_snippets WHERE id = ?
        """, (doc.metadata["snippet_id"],)).fetchone()

        if row:
            matches.append({
                "id": row["id"],
                "repository_id": row["repository_id"],
                "file_path": row["file_path"],
                "code_preview": row["code"][:300],
                "similarity_score": float(score),
            })

    conn.close()
    save_search_history(query, len(matches))

    return {"query": query, "count": len(matches), "results": matches}

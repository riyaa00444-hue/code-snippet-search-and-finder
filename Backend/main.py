import os
import ast
import sqlite3
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI



load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
VECTOR_DIR = os.path.join(BASE_DIR, "vector_store")

os.makedirs(VECTOR_DIR, exist_ok=True)


app = FastAPI(title="Code Snippet Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class AddRepositoryRequest(BaseModel):
    name: str
    path: str


def analyze_repository(repo_path: str):
    if not os.path.exists(repo_path):
        raise HTTPException(400, "Repository path does not exist")

    files = []
    for root, _, filenames in os.walk(repo_path):
        if "node_modules" in root or ".git" in root:
            continue
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), repo_path))

    description = "Repository analysis not available"
    if GOOGLE_API_KEY:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=GOOGLE_API_KEY,
        )
        description = llm.invoke(
            f"Explain briefly what this repository does:\n{files[:30]}"
        ).content

    return description, files


def parse_code_file(file_path: str) -> List[str]:
    """Parse Python with AST, fallback to whole file for JS/TS"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    if file_path.endswith(".py"):
        try:
            tree = ast.parse(source)
            snippets = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    snippets.append(ast.get_source_segment(source, node))
            return snippets or [source]
        except Exception:
            return [source]

    return [source]


def get_code_snippet_by_id(snippet_id: int):
    conn = get_db()
    row = conn.execute("""
        SELECT cs.id, cs.code, cs.file_path, r.name AS repository_name
        FROM code_snippets cs
        JOIN repositories r ON cs.repository_id = r.id
        WHERE cs.id = ?
    """, (snippet_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_search_history():
    conn = get_db()
    rows = conn.execute("""
        SELECT id, query, result_count, searched_at
        FROM search_history
        ORDER BY searched_at DESC
    """).fetchall()
    conn.close()

    return [dict(r) for r in rows]


def delete_search_history(history_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM search_history WHERE id = ?",
        (history_id,)
    )
    conn.commit()
    conn.close()



@app.post("/api/repositories")
def add_repository(repo: AddRepositoryRequest):
    desc, files = analyze_repository(repo.path)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO repositories
    (name, path, description, file_list, file_count, analyzed_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        repo.name,
        repo.path,
        desc,
        ",".join(files),
        len(files),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()
    return {"status": "added", "files": len(files)}


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
        raise HTTPException(404, "Repository not found")

    return dict(repo)


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
            if f.lower().endswith((".py", ".js", ".jsx", ".ts", ".tsx")):
                snippets += parse_code_file(os.path.join(root, f))

    if not snippets:
        raise HTTPException(400, "No code files found")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    metadatas = []
    for code in snippets:
        cur = conn.execute("""
        INSERT INTO code_snippets (repository_id, file_path, code)
        VALUES (?, ?, ?)
        """, (repo_id, repo["path"], code))
        metadatas.append({
            "snippet_id": cur.lastrowid,
            "repository_id": repo_id
        })

    FAISS.from_texts(snippets, embeddings, metadatas).save_local(VECTOR_DIR)

    conn.execute(
        "UPDATE repositories SET indexed = 1 WHERE id = ?", (repo_id,)
    )
    conn.commit()
    conn.close()

    return {"status": "indexed", "snippets": len(snippets)}


@app.get("/api/search")
def search_code(
    query: str = Query(..., min_length=3),
    repoId: Optional[int] = Query(None),
):
    index_path = os.path.join(VECTOR_DIR, "index.faiss")
    if not os.path.exists(index_path):
        raise HTTPException(
            400, "Search index not found. Index a repository first."
        )

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
        meta = doc.metadata or {}
        if repoId and int(meta.get("repository_id", -1)) != int(repoId):
            continue

        row = conn.execute("""
        SELECT id, repository_id, file_path, code
        FROM code_snippets WHERE id = ?
        """, (meta.get("snippet_id"),)).fetchone()

        if row:
            matches.append({
                "id": row["id"],
                "repository_id": row["repository_id"],
                "file_path": row["file_path"],
                "code_preview": row["code"][:300],
                "similarity_score": float(score),
            })

    conn.close()
    return {"query": query, "count": len(matches), "results": matches}


@app.get("/api/code/{snippet_id}")
def get_code_detail(snippet_id: int):
    snippet = get_code_snippet_by_id(snippet_id)
    if not snippet:
        raise HTTPException(404, "Code snippet not found")
    return snippet


@app.post("/api/code/{snippet_id}/explain")
def explain_code(snippet_id: int):
    snippet = get_code_snippet_by_id(snippet_id)
    if not snippet:
        raise HTTPException(404, "Code snippet not found")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY,
    )

    explanation = llm.invoke(f"""
Repository: {snippet['repository_name']}
File: {snippet['file_path']}

Explain this code:
{snippet['code']}
""").content

    return {"snippet_id": snippet_id, "explanation": explanation}


@app.get("/api/history")
def fetch_history():
    return get_search_history()


@app.delete("/api/history/{history_id}")
def remove_history(history_id: int):
    delete_search_history(history_id)
    return {"status": "deleted"}


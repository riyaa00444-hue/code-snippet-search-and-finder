import os
import ast
import sqlite3
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# ================= ENV =================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
VECTOR_DIR = os.path.join(BASE_DIR, "vector_store")

os.makedirs(VECTOR_DIR, exist_ok=True)

# ================= APP =================
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
        code TEXT,
        symbol_name TEXT,
        start_line INTEGER,
        end_line INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()

class AddRepositoryRequest(BaseModel):
    name: str
    path: str
    type: str


class RepositoryResponse(BaseModel):
    id: int
    name: str
    description: str
    file_list: List[str]
    analyzed_at: str


def analyze_repository(repo_path: str):
    if not os.path.exists(repo_path):
        raise HTTPException(400, "Repository path does not exist")

    files = []
    for root, _, filenames in os.walk(repo_path):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), repo_path))

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY,
    )

    prompt = f"Explain briefly what this repository does:\n{files[:30]}"
    description = llm.invoke(prompt).content

    return description, files


def save_repository(name, path, description, files):
    conn = get_db()
    cur = conn.cursor()

    now = datetime.utcnow().isoformat()
    cur.execute("""
    INSERT INTO repositories
    (name, path, description, file_list, file_count, analyzed_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, path, description, ",".join(files), len(files), now))

    repo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return repo_id, now

@app.post("/api/repositories", response_model=RepositoryResponse)
def add_repository(repo: AddRepositoryRequest):
    desc, files = analyze_repository(repo.path)
    repo_id, analyzed_at = save_repository(repo.name, repo.path, desc, files)

    return {
        "id": repo_id,
        "name": repo.name,
        "description": desc,
        "file_list": files,
        "analyzed_at": analyzed_at
    }


@app.get("/api/repositories")
def list_repositories():
    conn = get_db()
    rows = conn.execute("SELECT * FROM repositories").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def parse_python_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    tree = ast.parse(source)
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            chunks.append({
                "name": node.name,
                "code": ast.get_source_segment(source, node),
                "start": node.lineno,
                "end": node.end_lineno,
            })

    return chunks

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
        for f in files:
            if f.endswith(".py"):
                snippets += parse_python_file(os.path.join(root, f))

    if not snippets:
        raise HTTPException(400, "No code files found")

    texts = [s["code"] for s in snippets]

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )

        vector_store = FAISS.from_texts(texts, embeddings)
        vector_store.save_local(VECTOR_DIR)

    except Exception:
        # quota-safe fallback
        pass

    for s in snippets:
        conn.execute("""
        INSERT INTO code_snippets
        (repository_id, file_path, code, symbol_name, start_line, end_line)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            repo_id,
            repo["path"],
            s["code"],
            s["name"],
            s["start"],
            s["end"],
        ))

    conn.execute(
        "UPDATE repositories SET indexed = 1 WHERE id = ?", (repo_id,)
    )

    conn.commit()
    conn.close()

    return {
        "status": "indexed",
        "snippets_count": len(snippets)
    }

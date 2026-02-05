import os
import sqlite3
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

# -------------------- ENV --------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in .env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

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
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            description TEXT,
            file_list TEXT,
            file_count INTEGER,
            indexed INTEGER DEFAULT 0,
            analyzed_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


init_db()

# -------------------- SCHEMAS --------------------
class AddRepositoryRequest(BaseModel):
    name: str
    path: str
    type: str  # "connect" or "upload"


class RepositoryResponse(BaseModel):
    id: int
    name: str
    description: str
    file_list: List[str]
    analyzed_at: str

# -------------------- HELPERS --------------------
def analyze_repository(repo_path: str) -> dict:
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")

    files = []
    for root, _, filenames in os.walk(repo_path):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), repo_path))

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY,
    )

    prompt = f"""
    You are analyzing a code repository.

    File list:
    {files[:50]}

    Explain briefly:
    - What this repository does
    - What kind of project it is
    """

    response = llm.invoke(prompt)

    return {
        "description": response.content,
        "files": files,
    }


def save_repository(
    name: str,
    path: str,
    description: str,
    files: List[str],
):
    conn = get_db()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO repositories
        (user_id, name, path, description, file_list, file_count, indexed, analyzed_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,  # temporary user_id
            name,
            path,
            description,
            ",".join(files),
            len(files),
            0,
            now,
            now,
            now,
        ),
    )

    repo_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return repo_id, now

# -------------------- API --------------------
@app.post("/api/repositories", response_model=RepositoryResponse)
def add_repository(repo: AddRepositoryRequest):
    try:
        analysis = analyze_repository(repo.path)

        repo_id, analyzed_at = save_repository(
            name=repo.name,
            path=repo.path,
            description=analysis["description"],
            files=analysis["files"],
        )

        return {
            "id": repo_id,
            "name": repo.name,
            "description": analysis["description"],
            "file_list": analysis["files"],
            "analyzed_at": analyzed_at,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

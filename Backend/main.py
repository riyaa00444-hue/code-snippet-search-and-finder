import os
import ast
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends
from sqlalchemy.orm import Session

from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse   
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()



class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    path = Column(String)
    description = Column(Text)
    file_list = Column(Text)
    file_count = Column(Integer)
    indexed = Column(Boolean, default=False)
    analyzed_at = Column(String)


class CodeSnippet(Base):
    __tablename__ = "code_snippets"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer)
    file_path = Column(String)
    code = Column(Text)


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    result_count = Column(Integer)
    searched_at = Column(String)

Base.metadata.create_all(bind=engine)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_DIR = os.path.join(BASE_DIR, "vector_store")

os.makedirs(VECTOR_DIR, exist_ok=True)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI(title="Code Snippet Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




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



def delete_vector_store():
    index_path = os.path.join(VECTOR_DIR, "index.faiss")
    pkl_path = os.path.join(VECTOR_DIR, "index.pkl")

    if os.path.exists(index_path):
        os.remove(index_path)
    if os.path.exists(pkl_path):
        os.remove(pkl_path)



# ---------------- ROUTES ----------------

@app.post("/api/repositories")
def add_repository(
    repo: AddRepositoryRequest,
    db: Session = Depends(get_db)
):
    desc, files = analyze_repository(repo.path)

    new_repo = Repository(
        name=repo.name,
        path=repo.path,
        description=desc,
        file_list=",".join(files),
        file_count=len(files),
        analyzed_at=datetime.utcnow().isoformat()
    )

    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

    return {"status": "added", "files": len(files)}



@app.get("/api/repositories")
def list_repositories(db: Session = Depends(get_db)):
    repositories = db.query(Repository).all()
    return repositories



@app.get("/api/repositories/{repo_id}")
def get_repository_detail(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        raise HTTPException(404, "Repository not found")

    return repo

@app.get(
    "/api/repositories/{repo_id}/file",
    response_class=PlainTextResponse
)

def get_repository_file(
    repo_id: int,
    path: str = Query(...),
    db: Session = Depends(get_db)
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        raise HTTPException(404, "Repository not found")

  
    clean_path = path.strip()
    clean_path = clean_path.strip('"')
    clean_path = clean_path.strip("'")
    clean_path = clean_path.replace("\\", "/")

    base_path = os.path.abspath(repo.path)
    file_path = os.path.abspath(os.path.join(base_path, clean_path))

    if not file_path.startswith(base_path):
        raise HTTPException(400, "Invalid file path")

    if not os.path.isfile(file_path):
        raise HTTPException(404, "File not found")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()




@app.post("/api/repositories/{repo_id}/index")
def index_repository(repo_id: int, db: Session = Depends(get_db)):

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        raise HTTPException(404, "Repository not found")

    snippets = []

    for root, _, files in os.walk(repo.path):
        if "node_modules" in root or ".git" in root:
            continue
        for f in files:
            if f.lower().endswith((".py", ".js", ".jsx", ".ts", ".tsx")):
                snippets += parse_code_file(os.path.join(root, f))

    if not snippets:
        raise HTTPException(400, "No code files found")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )


    metadatas = []

    for code in snippets:
        snippet = CodeSnippet(
            repository_id=repo_id,
            file_path=repo.path,
            code=code
        )
        db.add(snippet)
        db.flush()  

        metadatas.append({
            "snippet_id": snippet.id,
            "repository_id": repo_id
        })

    FAISS.from_texts(snippets, embeddings, metadatas).save_local(VECTOR_DIR)

    repo.indexed = True
    db.commit()

    return {"status": "indexed", "snippets": len(snippets)}

@app.get("/api/search")
def search_code(
    query: str = Query(..., min_length=3),
    repoId: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    index_path = os.path.join(VECTOR_DIR, "index.faiss")
    if not os.path.exists(index_path):
        raise HTTPException(400, "Search index not found")

    embeddings = GoogleGenerativeAIEmbeddings(
       model="gemini-embedding-001",
       google_api_key=GOOGLE_API_KEY
)


    vector_store = FAISS.load_local(
        VECTOR_DIR, embeddings, allow_dangerous_deserialization=True
    )

    results = vector_store.similarity_search_with_score(query, k=5)

    matches = []

    for doc, score in results:
        meta = doc.metadata or {}

        if repoId and int(meta.get("repository_id", -1)) != int(repoId):
            continue

        snippet = db.query(CodeSnippet).filter(
            CodeSnippet.id == meta.get("snippet_id")
        ).first()

        if snippet:
            matches.append({
                "id": snippet.id,
                "repository_id": snippet.repository_id,
                "file_path": snippet.file_path,
                "code_preview": snippet.code[:300],
                "similarity_score": float(score),
            })

    history_entry = SearchHistory(
        query=query,
        result_count=len(matches),
        searched_at=datetime.utcnow().isoformat()
    )

    db.add(history_entry)
    db.commit()

    return {"query": query, "count": len(matches), "results": matches}




@app.get("/api/code/{snippet_id}")
def get_code_detail(snippet_id: int, db: Session = Depends(get_db)):
    snippet = db.query(CodeSnippet).filter(
        CodeSnippet.id == snippet_id
    ).first()

    if not snippet:
        raise HTTPException(404, "Code snippet not found")

    repo = db.query(Repository).filter(
        Repository.id == snippet.repository_id
    ).first()

    return {
        "id": snippet.id,
        "repository_id": snippet.repository_id,
        "file_path": snippet.file_path,
        "code": snippet.code,
        "repository_name": repo.name if repo else None
    }



@app.post("/api/code/{snippet_id}/explain")
def explain_code(snippet_id: int, db: Session = Depends(get_db)):
    snippet = db.query(CodeSnippet).filter(
        CodeSnippet.id == snippet_id
    ).first()

    if not snippet:
        raise HTTPException(404, "Code snippet not found")

    repo = db.query(Repository).filter(
        Repository.id == snippet.repository_id
    ).first()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY,
    )

    explanation = llm.invoke(f"""
Repository: {repo.name if repo else 'Unknown'}
File: {snippet.file_path}

Explain this code:
{snippet.code}
""").content

    return {"snippet_id": snippet_id, "explanation": explanation}



@app.get("/api/history")
def fetch_history(db: Session = Depends(get_db)):
    history = db.query(SearchHistory).order_by(
        SearchHistory.searched_at.desc()
    ).all()
    return history



@app.delete("/api/history/{history_id}")
def remove_history(history_id: int, db: Session = Depends(get_db)):
    history = db.query(SearchHistory).filter(
        SearchHistory.id == history_id
    ).first()

    if not history:
        raise HTTPException(404, "History not found")

    db.delete(history)
    db.commit()

    return {"status": "deleted"}



@app.delete("/api/repositories/{repo_id}")
def delete_repository(repo_id: int, db: Session = Depends(get_db)):

    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        raise HTTPException(404, "Repository not found")

  
    db.query(CodeSnippet).filter(
        CodeSnippet.repository_id == repo_id
    ).delete()


    db.delete(repo)

    db.commit()

   
    delete_vector_store()                                                      

    return {"message": "Repository deleted successfully"}                                                          
# Code Snippet Search and Finder

---

## Project Overview

A web application that allows developers to search through code repositories using natural language queries. Users can upload or connect code repositories, and the system automatically analyzes repositories with LLM to extract context and file structure. The system uses semantic search powered by LangChain and LLMs to find relevant functions, patterns, or implementations. The application provides code explanations and allows users to copy code snippets with proper attribution.

---

## Features

- User authentication with Firebase
- Upload or connect code repositories
- LLM-powered repository analysis (analyze repository context)
- Index code files automatically
- Natural language search interface
- Semantic code search using embeddings
- Display search results with code preview
- Code explanation using LLM
- Copy code snippets with attribution
- View usage examples
- Repository management (add, remove, list)
- Code file browser
- Search history
- Export search results

---

## Technology Stack

### Frontend
- React 19
- Vite (build tool)
- Tailwind CSS (styling)
- React Router DOM (routing)
- Axios or Fetch (API calls)
- Code syntax highlighting library (Prism.js or highlight.js)

### Backend
- Python 3.12+
- FastAPI (REST API)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Python AST (for code parsing)

### Database
- SQLite (for code metadata, repository info with LLM context, user data, search history)
- Vector Store: FAISS, ChromaDB, or Pinecone (for code embeddings ONLY - NOT stored in SQLite)

### Authentication
- Firebase Authentication (email/password)
- Firebase SDK in frontend

### AI/ML
- LangChain (for embeddings, semantic search, code analysis, repository analysis)
- Google Gemini LLM (for code explanations, understanding, and repository context analysis)
- Vector store (FAISS, ChromaDB, or Pinecone for code embeddings ONLY)
- Text embeddings (for converting code and queries to vectors)

---

## Architecture

### Database Architecture

**SQLite Database (Metadata Only):**
- `repositories` - Repository metadata with LLM-analyzed context (description, file_list, analyzed_at)
- `code_snippets` - Code text and metadata (file path, language, function/class name, line numbers)
- `search_history` - User search query history

**Vector Store (Embeddings Only):**
- Stores code embeddings with code_snippet_id reference
- Links to SQLite via code_snippet_id
- NOT stored in SQLite database

### Data Flow

```
User Action → Frontend Component → API Call → Backend Endpoint → Database/LLM/Vector Store → Response → UI Update
```

**Example Flow:**
```
Search Query → SearchBar → GET /api/search → FastAPI → LangChain (embeddings) → Vector Store (similarity search) → Results → Display in SearchResults
```

---

## API Endpoints

| Method | Endpoint                    | Protected | Purpose                                         | LLM Integration |
| ------ | --------------------------- | --------- | ----------------------------------------------- | --------------- |
| POST   | /api/repositories           | Yes       | Upload/add repository and analyze with LLM      | Yes             |
| GET    | /api/repositories           | Yes       | Get all user repositories                       | No              |
| GET    | /api/repositories/:id       | Yes       | Get repository details                          | No              |
| DELETE | /api/repositories/:id       | Yes       | Remove repository                               | No              |
| POST   | /api/repositories/:id/index | Yes       | Index repository code                           | Yes             |
| GET    | /api/search                 | Yes       | Search code snippets                            | Yes             |
| GET    | /api/code/:id               | Yes       | Get code snippet details                        | No              |
| POST   | /api/code/:id/explain       | Yes       | Get code explanation                            | Yes             |
| GET    | /api/history                | Yes       | Get search history                              | No              |
| DELETE | /api/history/:id            | Yes       | Clear search history item                       | No              |

---

## Frontend Structure

### Pages

| Page Name         | Route             | Protected | Main Components                         |
| ----------------- | ----------------- | --------- | --------------------------------------- |
| Landing           | /                 | No        | Navbar, Hero, Features, Footer          |
| Signup            | /signup           | No        | SignupForm                              |
| Login             | /login            | No        | LoginForm                               |
| Dashboard         | /dashboard        | Yes       | Navbar, RepositoryList, AddRepoButton   |
| Repository Detail | /repositories/:id | Yes       | RepositoryView, FileTree, CodeViewer    |
| Search            | /search           | Yes       | SearchBar, SearchResults, CodeCard      |
| Code Detail       | /code/:id         | Yes       | CodeViewer, CodeExplanation, CopyButton |
| History           | /history          | Yes       | HistoryList, HistoryItem                |

### Components

- **Navbar** - Navigation header (used on all pages)
- **Hero** - Hero section with CTA (Landing page)
- **Features** - Feature showcase (Landing page)
- **Footer** - Footer with links (all pages)
- **SignupForm** - Registration form (Signup page)
- **LoginForm** - Login form (Login page)
- **RepositoryList** - Display repositories (Dashboard)
- **RepositoryCard** - Single repository card (Dashboard)
- **AddRepoButton** - Add repository trigger (Dashboard)
- **AddRepoModal** - Add repository interface (Dashboard)
- **RepositoryView** - Repository overview (Repository Detail)
- **FileTree** - File browser (Repository Detail)
- **CodeViewer** - Display code with syntax highlighting (Repository Detail, Code Detail)
- **SearchBar** - Search input interface (Search page)
- **SearchResults** - Display search results (Search page)
- **CodeCard** - Code snippet card (Search page)
- **CodeExplanation** - Display AI explanation (Code Detail)
- **CopyButton** - Copy code with attribution (Code Detail, CodeCard)
- **HistoryList** - Display search history (History page)
- **HistoryItem** - Single history item (History page)
- **LoadingSpinner** - Loading indicator (multiple pages)
- **ErrorMessage** - Error display (multiple pages)
- **ProgressBar** - Indexing progress (Repository Detail)

---

## Issue Flow

### Foundation Phase (Issues 1-8)
1. **Project Setup** - Initialize project structure and dependencies
2. **Landing Page UI** - Create static landing page
3. **Signup Page UI** - Create static signup form
4. **Login Page UI** - Create static login form
5. **Firebase Auth Setup** - Configure Firebase project and SDK
6. **Integrate Signup with Firebase** - Connect signup form to Firebase
7. **Integrate Login with Firebase** - Connect login form to Firebase
8. **Dashboard UI** - Create protected dashboard page

### Core Features Phase (Issues 9-13)
9. **Add Repository Feature** - Implement repository addition with LLM analysis (Combined F+B)
10. **Code Indexing Backend** - Implement code parsing and embedding creation
11. **Repository Detail Page** - Create repository detail page with file browser (Combined F+B)
12. **Search Feature** - Implement semantic code search (Combined F+B)
13. **Code Detail Page** - Create code detail page with explanations (Combined F+B)

### Advanced Features Phase (Issues 14-16)
14. **Search History** - Implement search history feature (Combined F+B)
15. **Delete Repository** - Implement repository deletion
16. **Export Feature** - Implement export functionality

### Final Phase (Issue 17)
17. **Final Testing** - Complete application flow verification and documentation

---

## Key Concepts

### Semantic Search
- Uses embeddings to convert code and queries to vectors
- Performs similarity search in vector store
- Returns results ranked by semantic similarity, not just keywords

### LLM-Powered Analysis
- Repository analysis: Extracts context, description, and file list
- Code explanation: Generates explanations using repository context
- Uses Google Gemini LLM via LangChain

### Vector Store Architecture
- Embeddings stored ONLY in vector store (FAISS/ChromaDB/Pinecone)
- NOT stored in SQLite database
- Links to SQLite via code_snippet_id
- Enables fast semantic similarity search

### Code Indexing Process
1. Parse code files to extract functions/classes
2. Create embeddings for each code chunk
3. Store embeddings in vector store
4. Store code metadata in SQLite database
5. Link vector store entries to database records

---

## Development Guidelines

- Start with simple code parsing, improve iteratively
- Test semantic search with various queries
- Optimize embedding creation for performance
- Use repository context for better LLM explanations
- Handle errors gracefully at every step
- Provide loading states for long operations
- Ensure responsive design across devices

---

## Next Steps

After completing all issues:

1. Review and test all features end-to-end
2. Optimize performance where needed
3. Add additional error handling if required
4. Polish UI/UX based on testing feedback
5. Document any additional features or improvements made

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Google Generative AI](https://ai.google.dev/docs)

---

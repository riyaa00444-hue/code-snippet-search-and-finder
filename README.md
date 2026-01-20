# Internship Project Template

This template includes a FastAPI backend with Google Gemini LLM integration and a React frontend with Tailwind CSS.

## Project Structure

```
.
├── Backend/                    # FastAPI backend application
│   ├── main.py                 # Main backend server file
│   ├── pyproject.toml          # Python project configuration
│   ├── requirements.txt        # Python dependencies
│   ├── uv.lock                 # UV lock file for dependency versions
│   ├── README.md               # Backend-specific documentation
│   └── .env                    # Environment variables (create this file)
│
└── Frontend/                   # React frontend application
    ├── public/
    │   └── vite.svg            # Vite logo
    ├── src/
    │   ├── components/
    │   │   └── QuoteGenerator.jsx  # Quote generator component
    │   ├── assets/
    │   │   └── react.svg       # React logo
    │   ├── App.jsx             # Main app component (layout wrapper)
    │   ├── App.css             # App-specific styles
    │   ├── main.jsx            # React entry point
    │   └── index.css           # Global styles with Tailwind
    ├── eslint.config.js        # ESLint configuration
    ├── index.html              # HTML entry point
    ├── package.json            # Node.js dependencies and scripts
    ├── package-lock.json       # npm lock file
    ├── postcss.config.js       # PostCSS configuration
    ├── tailwind.config.js      # Tailwind CSS configuration
    ├── vite.config.js          # Vite build tool configuration
    └── README.md               # Frontend-specific documentation
```

## Getting Started

### Clone the Repository

First, you need to clone this repository to your local machine. This will download all the project files to your computer.

**Repository URL:** https://github.com/progressionschool/internship-project-template

**On Windows:**

1. Open **Git Bash** (if you have Git installed) or **Command Prompt**
2. Navigate to the directory where you want to save the project:
   ```bash
   cd C:\Users\YourName\Desktop
   ```
   (Replace `YourName` with your actual username)
3. Clone the repository:
   ```bash
   git clone https://github.com/progressionschool/internship-project-template.git
   ```
4. Navigate into the project directory:
   ```bash
   cd internship-project-template
   ```

**On macOS:**

1. Open **Terminal** (you can find it in Applications > Utilities)
2. Navigate to the directory where you want to save the project:
   ```bash
   cd ~/Desktop
   ```
   (Or any other directory you prefer)
3. Clone the repository:
   ```bash
   git clone https://github.com/progressionschool/internship-project-template.git
   ```
4. Navigate into the project directory:
   ```bash
   cd internship-project-template
   ```

**Note:** Make sure you have Git installed on your system. If you don't have Git installed, download it from [git-scm.com](https://git-scm.com/downloads).

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **UV Package Manager** - Fast Python package installer (see installation below)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**
- **Google API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Backend Setup

### 1. Install UV Package Manager

Install UV using pip:

```bash
pip install uv
```

For alternative installation methods, see the [UV documentation](https://github.com/astral-sh/uv).

### 2. Navigate to Backend Directory

```bash
cd Backend
```

### 3. Create Virtual Environment

Create a virtual environment using UV:

```bash
uv venv
```

This will create a `.venv` folder in the Backend directory.

### 4. Activate Virtual Environment

Activate the virtual environment:

**On Windows:**
```bash
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### 5. Install Dependencies

Install all packages from `requirements.txt`:

```bash
uv add -r requirements.txt
```

### 6. Create Environment File

Create a `.env` file in the `Backend` directory:

```bash
# On macOS/Linux
touch .env

# On Windows
type nul > .env
```

Add your Google API key to the `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 7. Run the Backend Server

```bash
uvicorn main:app --reload
```

The backend server will start at: **http://localhost:8000**

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Random Quote Endpoint: http://localhost:8000/api/random-quote

## Frontend Setup

### 1. Navigate to Frontend Directory

Open a new terminal window and navigate to the Frontend directory:

```bash
cd Frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run the Frontend Development Server

```bash
npm run dev
```

The frontend will start at: **http://localhost:5173** (or another port if 5173 is busy)

## Testing the Connection

1. Make sure both servers are running:

   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173

2. Open your browser and go to: http://localhost:5173

3. Click the "Generate Quote" button

4. You should see a random inspirational quote generated by the AI!

## Available Endpoints

### Backend Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint
- `GET /api/random-quote` - Sample endpoint to connect Frontend and Backend (generates random quote using Gemini LLM)

## Development Commands

### Backend

```bash
# Run development server with auto-reload
uvicorn main:app --reload

# Run on specific port
uvicorn main:app --reload --port 8001
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Technologies Used

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Google Generative AI** - Gemini LLM integration
- **python-dotenv** - Environment variable management

### Frontend

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **ESLint** - Code linting

## Next Steps

Once everything is running fine, here are some steps to extend this template:

1. **Create your own backend endpoints**

   - Add new API endpoints in `Backend/main.py`
   - Use FastAPI decorators like `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`
   - Test your endpoints using the Swagger UI at http://localhost:8000/docs

2. **Integrate new endpoints to the frontend**

   - Create new components in `Frontend/src/components/` folder
   - Update `Frontend/src/App.jsx` to include your new components
   - Use `fetch()` or libraries like `axios` to make API calls
   - Handle loading states and errors appropriately
   - Update the UI to display the data from your new endpoints

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Google Generative AI Documentation](https://ai.google.dev/docs)

## License

This is a template project for educational purposes.

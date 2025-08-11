# DevBuddy - Multi-Agent RAG Chatbot for GitHub Repositories

DevBuddy is a full-stack application that analyzes GitHub repositories using a multi-agent RAG (Retrieval-Augmented Generation) system where users can paste a GitHub repository link, and the system will clone, parse, and index the code to answer contextual questions about the repository and project.

## 🚀 Features

- **Repository Analysis**: Clone and parse Python files using AST
- **Multi-Agent System**: Specialized agents for ingestion, retrieval, answering, and code modification
- **Vector Search**: Qdrant vector database with hybrid semantic and keyword search
- **AI-Powered Chat**: Answer questions about code structure, functions, and generate documentation
- **Code Generation**: Generate README files and code patches
- **Modern UI**: Next.js frontend with Tailwind CSS
- **Fully Containerized**: Docker and Docker Compose for easy deployment

## 🏗️ Architecture

### Backend (FastAPI)
- **Ingestion Agent**: Clones repos, parses Python files, generates embeddings
- **Retriever Agent**: Hybrid search (semantic + keyword) in Qdrant
- **Answer Agent**: Gemini 1.5 Flash for contextual responses
- **Modifier Agent**: Groq Mixtral for code generation and modifications

### Frontend (Next.js + Tailwind)
- Repository URL input
- Real-time chat interface
- Ingestion progress tracking
- Modern, responsive design

### Vector Database (Qdrant)
- Stores code embeddings with metadata
- Function/class level chunking
- File path and line number tracking

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, LangGraph
- **Frontend**: Next.js, Tailwind CSS, TypeScript
- **Vector DB**: Qdrant
- **LLMs**: Gemini 1.5 Flash, Groq Mixtral
- **Containerization**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys for:
  - **Gemini** (AI Studio): https://aistudio.google.com/app/apikey
  - **Groq**: https://console.groq.com/keys

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd DevBuddy
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start all services:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
DevBuddy/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Core services (Qdrant, Embeddings)
│   │   ├── agents/           # AI agents (Ingestion, Retrieval, Answer, Modifier)
│   │   ├── models/           # Pydantic schemas
│   │   └── utils/            # Utilities (Git, AST parsing)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # Next.js pages
│   │   └── styles/           # CSS styles
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/ingest` - Clone and process a GitHub repository
- `POST /api/chat` - Chat with the repository using natural language
- `GET /api/health` - Health check endpoint

### Request Examples

**Ingest Repository:**
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "branch": "main",
    "include_patterns": ["*.py"],
    "exclude_patterns": ["__pycache__", "*.pyc", ".git"]
  }'
```

**Chat with Repository:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the main function in app.py",
    "repo_url": "https://github.com/user/repo",
    "max_context_chunks": 10
  }'
```

## 🤖 Multi-Agent System

### Ingestion Agent
- Clones GitHub repositories
- Parses Python files using AST
- Chunks code at function/class level
- Generates embeddings using OpenAI
- Stores vectors in Qdrant

### Retriever Agent
- Hybrid search combining semantic and keyword matching
- Filters by repository URL
- Returns relevant code chunks with metadata

### Answer Agent (Gemini 1.5 Flash)
- Answers questions about codebase
- Provides explanations of functions and classes
- Suggests improvements and best practices

### Modifier Agent (Groq Mixtral)
- Generates code modifications
- Creates README files
- Suggests refactoring and improvements

## 🐳 Docker Configuration

The application is fully containerized with three services:

1. **Qdrant** - Vector database
2. **Backend** - FastAPI application
3. **Frontend** - Next.js application

All services are orchestrated via Docker Compose with proper networking and volume management.

## 🔍 Usage Examples

### Basic Repository Analysis
1. Paste a GitHub repository URL
2. Click "Ingest" to process the repository
3. Ask questions about the codebase

### Common Questions
- "What does the main function do?"
- "Explain the User class"
- "How is authentication handled?"
- "Generate a README for this project"
- "Suggest improvements for the error handling"

### Code Modification
- "Add error handling to the login function"
- "Refactor the database connection code"
- "Create a new API endpoint for user profiles"

## 🛠️ Development

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables
See `.env` for all required environment variables.

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

This project is open-source and welcomes contributions. Please feel free to submit issues and pull requests.

### Development Guidelines
1. Follow PEP 8 for Python code
2. Use TypeScript for frontend code
3. Add tests for new features
4. Update documentation as needed

## 📝 License

MIT License

## 🙏 Acknowledgments

- **LangChain** for the multi-agent framework
- **Qdrant** for the vector database
- **Gemini** and **Groq** for the LLM services
- **FastAPI** and **Next.js** for the web framework

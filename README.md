# DevLens — AI-Powered Code Intelligence Platform

> **Understand any codebase in minutes.** DevLens combines AST parsing, semantic vector search, and local LLM intelligence to auto-generate architecture diagrams, answer questions about your code, review it, and map its structure — all without sending your code to the cloud.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG Chat** | Ask questions about any codebase in plain English — powered by phi3 LLM with file+line citations |
| 🗺️ **Architecture Diagrams** | Auto-generated layered architecture maps with AI descriptions per node |
| 🔍 **Hybrid Search** | SQL exact-match + Qdrant vector ANN search, merged with Reciprocal Rank Fusion |
| 📁 **Folder Intelligence** | AI-explained folder responsibilities across up to 3 directory levels |
| 📊 **Stack Detector** | Auto-detects framework, language, database, entry points, and risks |
| 🔬 **Code Review** | AI-powered per-symbol security, performance, and correctness findings |
| ♻️ **Refactor Suggestions** | phi3-generated refactoring proposals with before/after code snippets |
| 🛤️ **Execution Traces** | Cross-layer call path visualization |
| 🗃️ **API / DB / Auth Maps** | Auto-discovered REST endpoints, database schemas, and auth flows |
| ⏱️ **30-Second Fallback** | Every AI call times out gracefully — deterministic results always returned |

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** + **Uvicorn** — async Python API
- **SQLAlchemy 2 (async)** + **PostgreSQL (pgvector)** — relational store
- **Qdrant** — vector similarity search (768-dim, cosine)
- **Redis** + **Celery** — background job processing
- **Tree-sitter** — AST parsing for Python, TypeScript, JavaScript, Go, etc.
- **Ollama** (local) — phi3 (LLM) + nomic-embed-text (embeddings)
- **httpx** — async HTTP client for Ollama native API

### Frontend
- **Next.js 14** + **React 18** — app router, SSR
- **TanStack Query** — data fetching and caching
- **Zustand** — client state management
- **Lucide React** — icon library
- **Tailwind CSS** — styling

### Infrastructure (Docker)
- `pgvector/pgvector:pg16` — PostgreSQL 16 with vector extension
- `redis:7-alpine` — message broker
- `qdrant/qdrant:v1.9.0` — vector database

---

## ⚙️ Prerequisites

Before installing, make sure you have:

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker Desktop** | Latest | Runs Postgres, Redis, Qdrant |
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |
| **Ollama** | Latest | Local LLM server |
| **Git** | Any | Cloning repositories |

---

## 🚀 Getting Started (First-Time Setup)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-org/DevLens.git
cd DevLens
```

### Step 2 — Pull Ollama Models

DevLens uses two local models. Pull them before starting:

```bash
# LLM for chat, code review, and analysis (3.8B params, ~2.2 GB)
ollama pull phi3

# Embedding model for semantic search (137M params, ~274 MB)
ollama pull nomic-embed-text
```

Verify they are ready:

```bash
ollama list
# Expected:
# NAME                    SIZE
# phi3:latest             2.2 GB
# nomic-embed-text:latest 274 MB
```

> **Keep Ollama running** in the background. On Windows it starts automatically — check the system tray. On macOS/Linux run `ollama serve`.

### Step 3 — Configure Environment

Copy the example env file for the backend:

```bash
cp backend/.env.example backend/.env.local
```

The default `.env.local` works out of the box for local development:

```env
DATABASE_URL=postgresql+asyncpg://devlens:devlens@localhost:5432/devlens_db
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
JWT_SECRET=devlens-local-secret-change-in-production-256bit
LITELLM_API_BASE=http://localhost:11434/v1
```

> ⚠️ **For production**, change `JWT_SECRET` to a cryptographically random 256-bit string.

### Step 4 — Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Step 5 — Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 6 — Start Everything

**On Windows (PowerShell) — single command:**

```powershell
.\start-dev.ps1
```

This script automatically:
1. Starts Docker containers (Postgres, Redis, Qdrant)
2. Waits for containers to be healthy
3. Starts the FastAPI backend on `http://localhost:8000`
4. Starts the Next.js frontend on `http://localhost:3000`

**Or manually (any OS), in 3 separate terminals:**

```bash
# Terminal 1 — Infrastructure
docker compose up -d postgres redis qdrant

# Terminal 2 — Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 — Frontend
cd frontend
npm run dev
```

### Step 7 — Open DevLens

Navigate to **http://localhost:3000**

---

## 🖥️ Using DevLens

### Ingesting a Repository

1. Open **http://localhost:3000**
2. Provide a GitHub URL, a local folder path, or upload a ZIP file
3. Click **Analyze** — the pipeline runs in the background

**Ingest pipeline stages:**

```
Stage 1 (15%)  → Clone / fetch repository source
Stage 2 (50%)  → Walk file tree, compute hashes, store files in Postgres
Stage 3 (75%)  → AST parse with Tree-sitter → symbols & imports indexed
Stage 4 (83%)  → Embed top-60 files with nomic-embed-text → Qdrant
Stage 5 (95%)  → AI: stack detection, architecture diagram, folder intelligence
Stage 6 (100%) → Ready!
```

> **Expected time:** Small repos (< 100 files) ~1-2 min. Large repos ~3-4 min max.
> The embedding stage has a 90-second hard cap — the pipeline never gets stuck.

### Chatting with Your Code

1. Open an ingested repository
2. Go to the **Chat** tab
3. Ask anything:
   - *"What does this project do?"*
   - *"Where is authentication handled?"*
   - *"Explain the ChatService class"*
   - *"Find all database queries"*

Responses include `[[file.py:line-line]]` citations you can click to jump to source.

> If phi3 takes longer than 30 seconds, a deterministic template answer is returned immediately. The API never hangs.

### Gamechanger Suite

| Tool | Action |
|------|--------|
| **Code Review** | AI inspects top symbols for security, performance, and correctness |
| **Refactor** | phi3 proposes extract-method, rename, simplify, type-safety improvements |
| **Architecture** | Layered diagram with AI descriptions per node |
| **Folder Intelligence** | Per-directory responsibility breakdown |
| **Dependency Graph** | Symbol-to-symbol dependency visualization |
| **Execution Trace** | Call-tree from entry points |
| **API Explorer** | Auto-discovered REST endpoint map |
| **Database Map** | Schema and relationship visualization |

### Checking AI Status

```
GET http://localhost:8000/api/v1/ai/status
```

```json
{
  "ollama_available": true,
  "fallback_mode": false,
  "models": {
    "llm": "phi3",
    "embedding": "nomic-embed-text",
    "embedding_dim": 768
  },
  "features": {
    "rag_chat": true,
    "code_review": true,
    "vector_search": true
  }
}
```

If `ollama_available` is `false`, all features fall back to deterministic responses automatically.

---

## 🧩 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│          (React 18 · TanStack Query · Zustand)           │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / WebSocket
┌────────────────────────▼────────────────────────────────┐
│               FastAPI Backend  :8000                     │
│                                                          │
│   ┌────────────┐  ┌──────────────────┐  ┌────────────┐  │
│   │  API v1    │  │   AI Gateway     │  │  Workers   │  │
│   │ 25 routes  │  │  30s timeout +   │  │  Celery +  │  │
│   │            │  │  fallback system │  │  Redis     │  │
│   └─────┬──────┘  └────────┬─────────┘  └─────┬──────┘  │
│         │                  │                   │          │
│   ┌─────▼──────────────────▼─────────┐  ┌─────▼──────┐  │
│   │         Services Layer           │  │  Ingest    │  │
│   │  chat / analysis / search /      │  │  Pipeline  │  │
│   │  gamechanger / parsing           │  │  5 stages  │  │
│   └──────────────────────────────────┘  └────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────────┐
        │                │                    │
┌───────▼──────┐ ┌───────▼────────┐ ┌─────────▼──────┐
│  PostgreSQL  │ │    Qdrant      │ │    Ollama       │
│  (pgvector) │ │  768-dim ANN   │ │  phi3 (LLM)     │
│  files,      │ │  code chunks   │ │  nomic-embed    │
│  symbols     │ │                │ │  (embeddings)   │
└──────────────┘ └────────────────┘ └────────────────┘
```

### AI Pipeline (Chat RAG)

```
User Question
     ↓
HybridSearchService   →  SQL exact match (Postgres)  +  ANN search (Qdrant)
                          merged via Reciprocal Rank Fusion (RRF)
     ↓
ContextAssembler      →  format [[file:line-line]] citation blocks (max 6000 chars)
     ↓
AnswerGenerator       →  phi3 via Ollama /api/generate  (30s timeout)
                          fallback: deterministic template answer
     ↓
Response              →  {message, citations[], suggested_followups[], ai_generated}
```

---

## 📁 Project Structure

```
DevLens/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app, CORS, startup
│   │   ├── api/v1/                     # HTTP endpoint handlers
│   │   │   ├── ai_status.py            # GET /ai/status
│   │   │   ├── analysis.py             # summary, architecture, folders
│   │   │   ├── chat.py                 # RAG chat endpoint
│   │   │   ├── gamechanger.py          # code-review, refactor, trace...
│   │   │   ├── search.py               # hybrid + smart DSL search
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── ollama_client.py    # OllamaClient: batch embeddings + LLM
│   │   │   │   ├── guardrails.py       # 6 system prompts + JSON validator
│   │   │   │   └── timeout_wrapper.py  # ai_with_fallback(coro, fallback, 30s)
│   │   │   ├── analysis/
│   │   │   │   ├── stack_detector.py   # Framework + AI narrative
│   │   │   │   ├── arch_generator.py   # Concurrent AI node descriptions
│   │   │   │   └── folder_analyzer.py  # Concurrent AI folder purposes
│   │   │   ├── chat/
│   │   │   │   ├── answer_generator.py # phi3 RAG answer with fallback
│   │   │   │   ├── context_assembler.py# Citation block formatter
│   │   │   │   └── retriever.py        # Hybrid search retriever
│   │   │   ├── search/
│   │   │   │   ├── vector_indexer.py   # Batch embed + Qdrant upsert/search
│   │   │   │   ├── hybrid_search.py    # SQL + vector + RRF fusion
│   │   │   │   └── dsl_parser.py       # kind:fn loc>100 DSL parser
│   │   │   ├── parsing/
│   │   │   │   └── indexer.py          # Tree-sitter AST symbol indexer
│   │   │   └── gamechanger/
│   │   │       ├── code_reviewer.py    # Concurrent phi3 per-symbol review
│   │   │       └── refactor_engine.py  # Concurrent phi3 refactor suggestions
│   │   ├── models/                     # SQLAlchemy ORM (Repo, File, Symbol, Job...)
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   └── workers/tasks.py            # Celery ingest pipeline (5 stages)
│   ├── alembic/                        # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js app router pages
│   │   ├── components/                 # React UI components
│   │   ├── lib/api.ts                  # Typed API client
│   │   └── types/api.ts                # TypeScript type definitions
│   └── package.json
├── docker-compose.yml                  # Postgres + Redis + Qdrant
├── start-dev.ps1                       # One-click Windows startup
└── README.md
```

---

## 🔌 API Reference

Full interactive docs: `http://localhost:8000/api/v1/docs`

### Repositories & Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/ai/status` | Ollama connectivity + feature flags |
| `POST` | `/ingest` | Start ingestion job |
| `GET` | `/jobs/{id}` | Job progress |
| `GET` | `/repos` | List repositories |
| `DELETE` | `/repos/{id}` | Delete repository |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/repos/{id}/summary` | Stack + metrics + AI narrative |
| `GET` | `/repos/{id}/architecture` | Layered diagram (AI node descriptions) |
| `GET` | `/repos/{id}/folders` | Folder intelligence (AI purposes) |
| `GET` | `/repos/{id}/files` | Full file tree |
| `GET` | `/repos/{id}/symbols` | Symbols (`?q=name&kind=function`) |

### Search & Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/repos/{id}/search/hybrid` | SQL + vector hybrid search |
| `POST` | `/repos/{id}/search/smart` | DSL search (`kind:class import:fastapi`) |
| `POST` | `/repos/{id}/chat` | RAG chat with phi3 |

### Gamechanger Suite
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/repos/{id}/code-review` | AI code quality audit |
| `POST` | `/repos/{id}/refactor` | Refactoring suggestions |
| `GET` | `/repos/{id}/onboarding` | Developer onboarding path |
| `GET` | `/repos/{id}/dependency-graph` | Symbol dependency graph |
| `GET` | `/repos/{id}/timeline` | Commit timeline |
| `GET` | `/repos/{id}/trace` | Execution call trace |
| `GET` | `/repos/{id}/endpoints` | REST API map |
| `GET` | `/repos/{id}/database` | Database schema |
| `GET` | `/repos/{id}/auth-flow` | Auth flow diagram |

---

## ⚡ AI Timeout & Fallback System

Every AI call is protected:

```python
result = await ai_with_fallback(
    ai_coro  = OllamaClient.generate_json(prompt, system),
    fallback = deterministic_result,   # instant, no IO
    timeout  = 30.0,                   # hard cap seconds
    context  = "chat_answer",          # for logging
)
```

| Scenario | Result |
|----------|--------|
| AI responds within 30s | ✅ AI-generated result returned |
| AI exceeds 30s | ⏱️ Fallback returned instantly |
| Any exception | ❌ Fallback returned instantly |
| Ollama offline | 🔌 Fallback returned instantly |

The API contract is never broken.

---

## 🔧 Configuration

All settings live in `backend/app/core/config.py` and are loaded from `backend/.env.local`:

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://devlens:devlens@localhost:5432/devlens_db` | Async Postgres |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `QDRANT_URL` | `http://localhost:6333` | Vector DB |
| `JWT_SECRET` | dev placeholder | **Change for production** |
| `LITELLM_API_BASE` | `http://localhost:11434/v1` | Ollama base URL |
| `LITELLM_MODEL` | `ollama/phi3` | LLM model |
| `LITELLM_EMBEDDING_MODEL` | `ollama/nomic-embed-text` | Embedding model |

---

## 🐛 Troubleshooting

### Backend fails to start
```bash
# Check container health
docker compose ps

# Restart containers
docker compose down && docker compose up -d

# Re-run migrations
cd backend && alembic upgrade head
```

### Stuck during ingestion
```bash
# Verify Ollama is running and models are loaded
curl http://localhost:11434/api/tags

# Check AI status endpoint
curl http://localhost:8000/api/v1/ai/status
```

### `ollama_available: false`
- Ollama is not running → start it from system tray (Windows) or `ollama serve`
- Models not pulled → run `ollama pull phi3` and `ollama pull nomic-embed-text`
- App still works fully with deterministic fallbacks

### Database migration errors
```bash
cd backend
alembic upgrade head
```

### Frontend cannot reach backend
Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` (defaults to `http://localhost:8000`).

---

## 🧑‍💻 Development Notes

### Adding a New Language
1. `pip install tree-sitter-<language>`
2. Register in `backend/app/services/parsing/indexer.py`

### Swapping the LLM
1. Pull the model: `ollama pull <model>`
2. Set `LLM_MODEL = "<model>"` in `backend/app/services/ai/ollama_client.py`

### Running Tests
```bash
cd backend
pytest
```

### Creating a DB Migration
```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

## 📄 License

MIT License — see `LICENSE` file for details.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai) — local LLM inference
- [phi3](https://huggingface.co/microsoft/phi-3) — Microsoft's 3.8B parameter LLM
- [nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1) — 768-dim open-source embedding model
- [Tree-sitter](https://tree-sitter.github.io) — incremental, error-tolerant parsing system
- [Qdrant](https://qdrant.tech) — vector similarity search engine
- [FastAPI](https://fastapi.tiangolo.com) — modern async Python web framework
- [Next.js](https://nextjs.org) — React framework for production


# 🛠️ DevLens — Complete Setup, Environment & Execution Guide

This comprehensive guide explains **how to configure, run, inspect, and test** DevLens step-by-step. It details all **environment variables**, **API keys (where to get them and fallbacks)**, **configuration files**, and **inspection walkthroughs**.

---

## 📌 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Environment Variables & Configuration Files](#-environment-variables--configuration-files)
3. [API Keys & LLM Provider Configuration](#-api-keys--llm-provider-configuration)
4. [Execution Modes](#-execution-modes)
   - [Mode A: Local Hybrid Dev Server (Recommended for Inspection)](#mode-a-local-hybrid-dev-server-recommended-for-inspection)
   - [Mode B: Production Docker Container Setup](#mode-b-production-docker-container-setup)
5. [Step-by-Step Dashboard Inspection Walkthrough](#-step-by-step-dashboard-inspection-walkthrough)
6. [Troubleshooting & Frequently Asked Questions](#-troubleshooting--frequently-asked-questions)

---

## 📋 Prerequisites

Before running DevLens, ensure you have the following installed:

- **Docker Desktop** (v24.0+ with Docker Compose v2+) — Required for PostgreSQL (pgvector), Redis, and Qdrant vector database.
- **Node.js** (v18.0+ or v20.0+) & `npm` — Required for running the Next.js 14 frontend.
- **Python** (v3.11+) & `pip` — Required for running the FastAPI backend locally.

---

## 🔑 Environment Variables & Configuration Files

DevLens uses environment variables to configure database connections, vector storage, API URLs, and LLM models.

### 1. Root Environment File (`.env`)
Create a `.env` file in the **root directory** of the project (`c:\Users\lenovo\Desktop\DevLens\.env`):

```env
# ==========================================
# DevLens Central Environment Configuration
# ==========================================

# Database Settings (PostgreSQL 16 with pgvector)
POSTGRES_USER=devlens
POSTGRES_PASSWORD=devlens_pass
POSTGRES_DB=devlens_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# SQLAlchemy Async Connection String
DATABASE_URL=postgresql+asyncpg://devlens:devlens_pass@localhost:5432/devlens_db

# Redis Message Broker & Pub/Sub
REDIS_URL=redis://localhost:6379/0

# Qdrant Vector Database Settings
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=devlens_code_chunks

# Local LLM & Embedding Model Settings (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=ollama/bge-m3
LLM_MODEL=ollama/deepseek-coder:6.7b-instruct

# Optional Cloud AI API Keys (Leave blank to use local Ollama / Mock AI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Frontend API Endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 2. Detailed Breakdown of Every Environment Variable

| Variable Name | Required? | Default Value | Description | Where to Get / How to Change |
|---------------|-----------|---------------|-------------|------------------------------|
| `POSTGRES_USER` | Yes | `devlens` | PostgreSQL database username | Choose any string for local dev |
| `POSTGRES_PASSWORD` | Yes | `devlens_pass` | PostgreSQL database password | Choose any secure string |
| `POSTGRES_DB` | Yes | `devlens_db` | PostgreSQL database name | Default database created on boot |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://devlens:devlens_pass@localhost:5432/devlens_db` | Async SQLAlchemy connection string | Must match user, pass, host, port, and db name |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection URL for Celery and Pub/Sub | Default local port 6379 |
| `QDRANT_URL` | Yes | `http://localhost:6333` | Qdrant vector database HTTP endpoint | Port 6333 (or Qdrant Cloud URL) |
| `QDRANT_COLLECTION` | Yes | `devlens_code_chunks` | Qdrant vector collection name | Internal collection name |
| `OLLAMA_BASE_URL` | Optional | `http://localhost:11434` | Local Ollama API server URL | Default port 11434 if Ollama installed |
| `EMBEDDING_MODEL` | Optional | `ollama/bge-m3` | Vector embedding model name | Ollama model name or OpenAI `text-embedding-3-small` |
| `LLM_MODEL` | Optional | `ollama/deepseek-coder:6.7b-instruct` | LLM model for grounded RAG chat & summaries | Ollama, OpenAI `gpt-4o-mini`, or Anthropic `claude-3-5-sonnet` |
| `OPENAI_API_KEY` | Optional | *(empty)* | OpenAI API Key for cloud GPT models | Get from [OpenAI Platform Keys](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | Optional | *(empty)* | Anthropic API Key for Claude models | Get from [Anthropic Console Keys](https://console.anthropic.com/settings/keys) |
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Frontend backend API URL | Point to FastAPI port (8000) |

---

## 🤖 API Keys & LLM Provider Configuration

DevLens is built with **zero mandatory external cloud dependencies**.

### Fallback Behavior:
- **If `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are empty**: DevLens automatically uses local **Ollama** models (`bge-m3` for embeddings, `deepseek-coder` for LLM).
- **If Ollama is not running**: DevLens falls back seamlessly to deterministic AI heuristics and structured fallback summaries so that **every single UI feature works 100% out of the box** for testing and demonstration!

### Optional: How to use Cloud OpenAI / Anthropic Models
If you want to use OpenAI or Anthropic for even richer LLM completions:

1. **OpenAI**:
   - Register/login at [OpenAI Platform](https://platform.openai.com/).
   - Navigate to **API Keys** -> **Create new secret key**.
   - Paste your key in `.env`:
     ```env
     OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
     LLM_MODEL=gpt-4o-mini
     EMBEDDING_MODEL=text-embedding-3-small
     ```

2. **Anthropic**:
   - Register/login at [Anthropic Console](https://console.anthropic.com/).
   - Navigate to **API Keys** -> **Create Key**.
   - Paste your key in `.env`:
     ```env
     ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
     LLM_MODEL=claude-3-5-sonnet-20241022
     ```

---

## 🚀 Execution Modes

### Mode A: Local Hybrid Dev Server (Recommended for Development & Inspection)

This mode runs background infrastructure in Docker containers while allowing live code editing for backend and frontend.

#### Step 1: Start Infrastructure Containers
Open a terminal in the project root (`c:\Users\lenovo\Desktop\DevLens`):

```bash
docker compose up -d postgres redis qdrant
```

*Verification*: Verify containers are running by typing `docker ps`. You should see `postgres` (port 5432), `redis` (port 6379), and `qdrant` (port 6333).

#### Step 2: Start Backend Server (FastAPI)
Open a new terminal window:

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

*Verification*: Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. You should see the interactive Swagger OpenAPI UI.

#### Step 3: Start Frontend Server (Next.js 14)
Open a third terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Run Next.js dev server
npm run dev
```

*Verification*: Open [http://localhost:3000](http://localhost:3000) in your browser. You should see the DevLens Ingestion dashboard.

---

### Mode B: Production Docker Container Setup

This mode runs the entire stack (PostgreSQL, Redis, Qdrant, FastAPI Backend, Celery Worker, Next.js Frontend, and Nginx Reverse Proxy) using a single command.

```bash
# Build and run all production services
docker compose -f docker-compose.prod.yml up -d --build
```

*Access Endpoints*:
- **DevLens Application**: [http://localhost](http://localhost) (Nginx port 80)
- **API Swagger Docs**: [http://localhost/api/v1/docs](http://localhost/api/v1/docs)

---

## 🖥️ Step-by-Step Dashboard Inspection Walkthrough

Follow these steps to test every single capability of DevLens:

### 1. Ingest a Repository
1. Navigate to [http://localhost:3000](http://localhost:3000).
2. Select **Local Folder** (or enter a Git repository URL).
3. Click **Ingest Repository**.
4. Observe real-time progress via WebSockets: `INGESTING` → `PARSING` → `EMBEDDING` → `ANALYZING` → `COMPLETE`.

### 2. Inspect Dashboard Feature Tabs
Once ingestion completes, click **View Repository Intelligence Dashboard** to explore the 13 feature tabs:

- **✨ AI Summary**: Inspect tech stack badges, complexity rating (1-10), onboarding hours estimate, key modules, entry points, and risks.
- **📐 Architecture Diagram**: Inspect 6-tier layered canvas (`presentation`, `api`, `business_logic`, `data_access`, `external`, `infrastructure`). Click any node to view file lists and AST symbols.
- **📁 Folder Intel**: Inspect folder purpose summaries, key files ranked by AST symbol centrality, and complexity ratings.
- **🔌 API Explorer**: Inspect REST routes with HTTP method badges (`GET`, `POST`), controller line links, middleware guards, and test execution using the live **"Try It Out"** runner console.
- **🗄️ DB Visualizer**: Inspect ORM database schema table cards, column data types, primary key/foreign key badges, and relationships.
- **🔒 Auth Flow**: Inspect the step-by-step visual security pipeline (Client -> Middleware Interceptor -> Token Verification -> Protected Route).
- **🚀 Execution Trace**: Inspect multi-tier call graph execution trees. Select entry targets (e.g. "Action: create_order") to view solid (1.0 confidence) vs dashed (0.7 confidence) edges, ORM database operations (`SELECT`/`INSERT`), and AI path explanations ("Why this path?").
- **🛡️ AI Code Review**: Inspect findings categorized by domain concerns (`security`, `performance`, `correctness`, `maintainability`) and severity filters.
- **🔧 AST Refactor**: Inspect AST cyclomatic & cognitive complexity metrics and proposed code refactoring diffs.
- **📜 Commit Timeline**: Scroll through chronological git commit eras with AI milestone summaries.
- **🔀 Arch Diff**: Inspect branch diff comparisons (base vs head) for added/removed APIs, schema modifications, and security risks.
- **🧩 Onboarding Path**: View topological 30-minute developer reading path with key file recommendations and checkpoint questions.
- **🕸️ Dependency Graph**: Search and inspect interactive symbol import connections across files.
- **💬 RAG Chat**: Ask questions ("Where is authentication handled?") and receive token-by-token streaming responses with inline citations (`[[file.py:10-25]]`).
- **🔍 Smart Search**: Execute structural query DSL strings (`kind:function`, `import:express`, `name:auth*`).

---

## ❓ Troubleshooting & Frequently Asked Questions

### Q1: "PostgreSQL port 5432 is already in use by another local Postgres service!"
**Solution**: Stop your local PostgreSQL service or change the host port mapping in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"
```
And update `DATABASE_URL` in `.env`:
`postgresql+asyncpg://devlens:devlens_pass@localhost:5433/devlens_db`

### Q2: "Celery task retries or Redis connection error"
**Solution**: Ensure Redis container is active: `docker compose up -d redis`.

### Q3: "Do I need to install Ollama or buy OpenAI keys to run DevLens?"
**Solution**: **No!** DevLens includes built-in deterministic fallbacks for code reviews, summaries, refactoring diffs, and execution traces so you can test and demonstrate the full app without spending a single dollar or installing external models.

---

## 🧪 Verification Commands

Run backend unit and integration tests at any time:

```bash
cd backend
pytest -v
```

All 10 test suites covering AST parsing, RAG pipeline, search DSL, API explorer, DB visualizer, execution trace, and V2 gamechanger features will execute cleanly!

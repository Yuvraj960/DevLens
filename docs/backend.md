# Backend Architecture & Services (docs/backend.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

The DevLens backend is built on **FastAPI (Python 3.11)** using an asynchronous design pattern with **SQLAlchemy 2.0 (asyncpg)** and **Celery** for background task execution.

```
backend/
├── app/
│   ├── api/v1/          # REST & WebSocket Endpoints
│   ├── core/            # Config, Security, Database, Logging
│   ├── models/          # SQLAlchemy ORM Models
│   ├── schemas/         # Pydantic Request/Response Models
│   ├── services/        # Domain Services (Ingestion, Parsing, Search)
│   ├── workers/         # Celery tasks and app configuration
│   ├── pipelines/       # LangGraph Agent DAGs
│   └── main.py          # FastAPI Application Factory
├── alembic/             # Database Migration Scripts
├── tests/               # Pytest Unit & Integration Tests
└── pyproject.toml       # Python Dependencies & Tool Configuration
```

---

## Core Subsystems

### 1. Application Factory (`app/main.py`)
- Initializes FastAPI app instance.
- Configures CORS middleware for frontend origin (`http://localhost:3000`).
- Attaches global exception handlers (RFC 7807 Problem Details).
- Registers `/api/v1` routes, `/ws` WebSocket router, and `/health`.

### 2. Configuration & Security (`app/core/`)
- `config.py`: Uses `pydantic-settings` to parse `.env` variables (`DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `JWT_SECRET`, `LITELLM_MODEL`).
- `database.py`: Constructs `create_async_engine()` and `async_sessionmaker()`.
- `security.py`: Handles JWT token generation/validation and API Key security dependencies.

### 3. Workers & Async Jobs (`app/workers/`)
- `celery_app.py`: Celery instance connected to Redis broker.
- `tasks.py`: Background tasks (e.g. `ingest_repo_task`).

---

## Quick Node Connections
- Data Models: [Database & Schema](database.md)
- Ingestion System: [Ingestion Pipeline](ingestion.md)
- API Specs: [API Contracts](api.md)

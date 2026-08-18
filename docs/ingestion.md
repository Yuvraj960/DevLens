# Ingestion Pipeline (docs/ingestion.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

The DevLens Ingestion Pipeline processes user-submitted codebases from GitHub URLs, uploaded ZIP archives, or local directories.

```
 User Input (URL / ZIP / Path)
             │
             ▼
   FastAPI POST /api/v1/ingest
             │
             ▼  Enqueues Job
     Celery Worker Task
   `ingest_repo_task(job_id)`
             │
 ┌───────────┴───────────┐
 ▼                       ▼
Fetch Repository      File Walk Engine
(git clone / unzip)   - Skip binaries / ignored paths
                      - Count LOC & compute SHA256
                      - Save File records to Postgres
             │
             ▼
 Emit Redis Pub/Sub Event -> WebSocket Client
```

---

## Key Rules & Filtering

- **Ignored Directory Patterns**: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `.next`, `.target`.
- **Binary File Detection**: File inspection checks for null bytes (`\x00`) in the first 8000 bytes.
- **Content Hashing**: SHA256 hash calculated per file content for incremental re-parsing in Phase 1.

---

## Quick Node Connections
- Ingestion Task Implementation: [Backend Architecture](backend.md)
- Job Schema: [Database & Schema](database.md)

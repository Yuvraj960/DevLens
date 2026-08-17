# API Contracts & Integration (docs/api.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

DevLens follows an OpenAPI 3.1 contract-first strategy documented in [API_CONTRACTS.md](../API_CONTRACTS.md).

```
API_CONTRACTS.md (OpenAPI 3.1 Spec)
          │
          ├──────────────────────────┐
          ▼                          ▼
FastAPI Router Routes        TypeScript Type Gen
(`app/api/v1/`)              (`frontend/src/types/api.d.ts`)
```

---

## Phase 0 Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ingest` | Initiates repository ingestion (`github`, `zip`, `folder`) |
| `GET` | `/api/v1/jobs/{job_id}` | Fetches job status & progress |
| `WS` | `/ws/jobs/{job_id}` | WebSocket stream for job status updates |
| `GET` | `/api/v1/repos` | Lists all ingested repositories |
| `GET` | `/api/v1/repos/{id}` | Gets repository details |
| `GET` | `/api/v1/repos/{id}/files` | Gets repository file tree hierarchy |
| `GET` | `/health` | Service health check |

---

## Quick Node Connections
- Backend Endpoints: [Backend Architecture](backend.md)
- Frontend Integration: [Frontend Architecture](frontend.md)

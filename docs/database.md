# Database & Data Models (docs/database.md)

[← Back to Knowledge Graph Index](README.md)

---

## Entity Relationship Topology

```
┌──────────────────┐       1:N       ┌──────────────────┐
│      repos       │─────────────────│      files       │
└────────┬─────────┘                 └────────┬─────────┘
         │                                    │
         │ 1:N                                │ 1:N
         ▼                                    ▼
┌──────────────────┐                 ┌──────────────────┐
│      jobs        │                 │     symbols      │
└──────────────────┘                 └──────────────────┘
```

---

## Table Schemas

### `repos`
- `id`: UUID (Primary Key)
- `name`: String (Repository name)
- `source_type`: String (`github`, `zip`, `folder`)
- `source_url`: String (Optional source URL or path)
- `default_branch`: String (e.g. `main`)
- `status`: String (`ingesting`, `ready`, `error`)
- `created_at`, `updated_at`: DateTime

### `files`
- `id`: UUID (Primary Key)
- `repo_id`: UUID (FK -> `repos.id`)
- `path`: String (Relative file path inside repo)
- `language`: String (`typescript`, `python`, `javascript`, `go`, etc.)
- `size_bytes`: Integer
- `loc`: Integer (Lines of code)
- `content_hash`: String (SHA256 hash of file content)
- `parsed_at`: DateTime (Nullable)

### `jobs`
- `id`: UUID (Primary Key)
- `repo_id`: UUID (FK -> `repos.id`)
- `status`: Enum (`QUEUED`, `CLONING`, `WALKING`, `PARSING`, `EMBEDDING`, `ANALYZING`, `COMPLETE`, `FAILED`)
- `stage`: String
- `progress`: Float (0 to 100)
- `message`: String
- `error`: String (Nullable)

---

## Quick Node Connections
- Backend ORM implementation: [Backend Architecture](backend.md)
- Ingestion pipeline writes: [Ingestion Pipeline](ingestion.md)

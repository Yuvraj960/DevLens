# System Architecture & AI Intelligence (docs/architecture.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

Phase 2 introduces automated system analysis, layered architecture diagramming, and folder intelligence analytics for ingested repositories.

```
                  Ingested Repository Data (Files & Symbols)
                                      │
                                      ▼
                        Analysis Pipeline Service
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
  StackDetector             ArchitectureGenerator             FolderAnalyzer
(Framework Fingerprinting) (Layer Clustering & Edges)   (Key File Centrality & Purpose)
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                                      ▼
                      PostgreSQL `repo_analyses` Table
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
  GET /summary                GET /architecture               GET /folders
  SummaryDashboard            ArchitectureCanvas              FolderIntelTree
```

---

## Architectural Layers

1. **`presentation`**: React/Next.js pages, UI components, HTML templates, CSS.
2. **`api`**: REST/GraphQL routers, controllers, middleware, handlers.
3. **`business_logic`**: Services, pipelines, workflows, domain models.
4. **`data_access`**: ORM entities, repositories, database queries, migrations.
5. **`external`**: External HTTP clients, third-party SDK integrations, APIs.
6. **`infrastructure`**: Docker, Redis, Celery, Qdrant, configuration setups.

---

## Quick Node Connections
- Data Store: [Database & Schema](database.md)
- Ingestion Pipeline: [Ingestion Pipeline](ingestion.md)
- API Contracts: [API Contracts](api.md)

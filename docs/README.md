# DevLens — Mindmap & Knowledge Graph (docs/README.md)

Welcome to the DevLens Documentation Knowledge Graph. This interconnected markdown network maps the architectural components, execution pipelines, database models, and API interfaces for the DevLens platform.

---

## 🗺️ System Mindmap Graph

```
                            ┌────────────────────────┐
                            │   DevLens Knowledge    │
                            │      [README.md]       │
                            └───────────┬────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
  ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
  │ Backend Framework  │     │ Database Schema    │     │ Ingestion Pipeline │
  │   [backend.md]     │     │   [database.md]    │     │   [ingestion.md]   │
  └──────────┬─────────┘     └──────────┬─────────┘     └──────────┬─────────┘
             │                          │                          │
             ├──────────────────────────┼──────────────────────────┤
             ▼                          ▼                          ▼
  ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
  │ Parsing & Symbols  │     │ API Contracts      │     │ Frontend App       │
  │   [parsing.md]     │     │     [api.md]       │     │   [frontend.md]    │
  └────────────────────┘     └────────────────────┘     └────────────────────┘
```

---

## 🗂️ Documentation Navigation Nodes

1. ⚙️ **[Backend Architecture](backend.md)** — FastAPI layout, app routing, security, structured logging, and Celery setup.
2. 📐 **[System Architecture & Intelligence](architecture.md)** — Automated stack fingerprinting, 6-tier layer clustering, and architecture graph.
3. 🗄️ **[Database & Models](database.md)** — PostgreSQL tables (`repos`, `files`, `symbols`, `imports`, `jobs`, `repo_analyses`), Alembic migrations, and pgvector.
4. 📥 **[Ingestion Pipeline](ingestion.md)** — GitHub cloning, ZIP extraction, local folder walking, content-hashing, and binary filters.
5. 🌳 **[Parsing & Indexing](parsing.md)** — Tree-sitter AST queries, symbol indexing, import graph resolution, and Qdrant vectors.
6. 💬 **[Grounded RAG Chat Engine](chat.md)** — Query expander, retriever, context assembler, citation enforcement (`[[file:line]]`), and SSE streams.
7. 🔍 **[Structural Smart Search DSL](search.md)** — Query DSL syntax (`kind:`, `import:`, `name:`), AST matching, and hybrid search.
8. 🔌 **[API Explorer, DB & Auth Engine](explorer.md)** — Route extraction, ORM ER diagram visualizer, Auth strategy mapper, and Execution trace engine.
9. 🚀 **[Flagship Execution Trace Engine](trace.md)** — Multi-tier BFS call graph traversal, confidence scoring, DB/API enricher, and visual trace canvas.
10. 🌟 **[V2 Gamechanger Intelligence Suite](v2_gamechanger.md)** — Code review agent, AST refactoring engine, commit timeline, arch diff, onboarding path, and dep graph.
11. 📜 **[API Contracts](api.md)** — OpenAPI 3.1 REST endpoints, WebSocket streams, and TypeScript client generation.
12. 🎨 **[Frontend Architecture](frontend.md)** — Next.js 14 App Router, Zustand UI state, TanStack Query, Monaco Editor, and React Flow.

---

## 📌 Related Files
- Main Architectural Spec: [PRD_SYSTEM_ARCHITECT.md](../PRD_SYSTEM_ARCHITECT.md)
- Development Decision Logs: [DEV_LOGS.md](../DEV_LOGS.md)
- Phase Roadmap: [ROADMAP.md](../ROADMAP.md)
- Project Rules: [CLAUDE.md](../CLAUDE.md)

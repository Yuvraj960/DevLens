# Production-Grade API Explorer, DB Visualizer & Auth Engine (docs/explorer.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

Phase 4 delivers production-grade repository intelligence tools: API Explorer, ORM Database ER Schema Visualizer, Auth & Security Pipeline Mapper, and End-to-End Execution Trace Engine.

```
                         Ingested Source Code
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
  ApiExtractor                DbExtractor                AuthExtractor
 (Routes & Schemas)         (ORM ER Tables)            (Security Pipeline)
       │                           │                           │
       ▼                           ▼                           ▼
 GET /endpoints              GET /database              GET /auth-flow
 ApiExplorer UI              DbVisualizer UI            AuthFlowMap UI
```

---

## Capabilities

1. **API Explorer**: Automatic route detection (`@router.get`, `app.post`, `route.ts`) with request/response schema inspect & interactive test runner.
2. **Database Schema Visualizer**: Extracts tables, columns, primary/foreign keys, and relationships across SQLAlchemy, Prisma, TypeORM, and Django.
3. **Auth & Security Mapper**: Maps authentication pipeline (Client -> Middleware -> JWT Verification -> Protected Handler).
4. **Execution Trace Engine**: Traces function call paths (`CallTraceNode`) from HTTP controllers to DB queries.

---

## Quick Node Connections
- Grounded RAG Chat: [Grounded RAG Chat](chat.md)
- Database & Models: [Database & Models](database.md)
- API Contracts: [API Contracts](api.md)

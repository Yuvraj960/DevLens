# Grounded RAG Chat Engine (docs/chat.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

Phase 3 introduces the codebase-grounded RAG chat engine with strict citation enforcement (`[[file.ts:10-25]]`) and real-time Server-Sent Events (SSE) token streaming.

```
       User Question ("Where is JWT verified?")
                         │
                         ▼
                   QueryExpander
        (Generates search variants & intent)
                         │
                         ▼
                     Retriever
        (Qdrant Vector + PostgreSQL Symbol Search)
                         │
                         ▼
                 ContextAssembler
        (Ranks, deduplicates & formats snippet window)
                         │
                         ▼
                  AnswerGenerator
        (Streaming LLM with strict citation rules)
                         │
                         ▼
        SSE Token Stream → ChatInterface UI
```

---

## Citation Protocol

Every assistant claim must include an inline citation:
- Format: `[[src/auth/jwt.ts:12-45]]`
- Frontend parsing: Renders as clickable badge opening code snippet modal.

---

## Quick Node Connections
- Search Engine: [Structural Search](search.md)
- Database & Models: [Database & Models](database.md)
- API Contracts: [API Contracts](api.md)

# Structural Query DSL & Smart Search Engine (docs/search.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

The Smart Search engine parses structural query DSL strings into combined AST symbol lookups, import graph queries, and Qdrant vector searches.

```
       Query DSL ("kind:function import:express name:auth*")
                         │
                         ▼
                     DSLParser
        (Parses filters: kind, import, name, loc)
                         │
                         ▼
                Query Execution Pipeline
        (PostgreSQL Symbol/Import GIN + Qdrant Vectors)
                         │
                         ▼
        SearchResponse → SmartSearchPanel UI
```

---

## Supported Query Syntax

| Filter Pattern | Example | Description |
|----------------|---------|-------------|
| `kind:<type>` | `kind:function`, `kind:class` | Filter AST symbol kinds |
| `import:<module>` | `import:express`, `import:stripe` | Filter files importing module |
| `name:<pattern>` | `name:auth*`, `name:User*` | Fuzzy or regex symbol name match |
| `loc:<range>` | `loc>50`, `loc<200` | Filter by file line count |

---

## Quick Node Connections
- RAG Chat: [Grounded RAG Chat](chat.md)
- Parsing Engine: [Parsing & Indexing](parsing.md)
- API Contracts: [API Contracts](api.md)

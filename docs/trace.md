# Flagship Execution Trace Engine & Multi-Tier Visualization (docs/trace.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

Phase 5 delivers the flagship feature of **DevLens**: end-to-end execution path tracing from user interface interactions (`onClick`, `onSubmit`) down through API gateways, controllers, business services, ORM repositories, and database/external API calls.

```
┌───────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐     ┌───────────────┐
│ UI Action │ ──► │ API Gateway │ ──► │ Middleware  │ ──► │ Controller │ ──► │ Service   │ ──► │ ORM Repo     │ ──► │ DB / External │
└───────────┘     └─────────────┘     └─────────────┘     └────────────┘     └───────────┘     └──────────────┘     └───────────────┘
```

---

## Trace Pipeline Architecture

1. **`EntryResolver`**: Resolves start nodes from UI action handlers (`onClick`), HTTP endpoints (`@router.get`), or worker tasks.
2. **`PathTraverser`**: Performs BFS traversal with cycle detection and assigns edge confidence scores (1.0 solid vs 0.7 dashed).
3. **`PathEnricher`**: Enriches nodes with DB ORM operations (`SELECT`, `INSERT`), external HTTP client calls (`fetch`, `httpx`), and AI explanations.
4. **`FlagshipTraceCanvas`**: Interactive multi-tier React Flow style visual layout.

---

## Quick Node Connections
- API Explorer: [API Explorer & DB Engine](explorer.md)
- System Architecture: [System Architecture & Intelligence](architecture.md)
- API Contracts: [API Contracts](api.md)

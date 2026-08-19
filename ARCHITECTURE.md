# 📐 DevLens — Condensed System Architecture Specification

DevLens is a production-grade code intelligence platform that converts raw code repositories into interactive, layered mental models, grounded AI chat engines, and multi-tier call graph visualizers.

---

## 🏛️ System High-Level Topology

```
                                  +-----------------------+
                                  |   Next.js 14 Client   |
                                  +-----------+-----------+
                                              | (HTTP / SSE / WS)
                                              v
                                  +-----------+-----------+
                                  | Nginx Reverse Proxy   |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
        +------------+------------+                       +------------+------------+
        |   FastAPI REST Engine   |                       | Celery Ingestion Worker |
        +------------+------------+                       +------------+------------+
                     |                                                 |
        +------------+------------+                       +------------+------------+
        | SQLAlchemy 2.0 Async    |                       | Tree-sitter AST Parser    |
        +------------+------------+                       +------------+------------+
                     |                                                 |
        +------------+------------+                       +------------+------------+
        | PostgreSQL 16 (pgvector)|                       |  Qdrant Vector DB (bge-m3)|
        +-------------------------+                       +-------------------------+
```

---

## 🔁 Core Data Processing Flow

1. **Ingestion & Deduplication (`IngestionService`)**: Clones/unzips codebases, computes per-file SHA256 content hashes, skips unchanged files, and filters null-byte binaries.
2. **Multi-Language AST Parsing (`LanguageManager`)**: Passes AST symbols into `TSParser`, `PythonParser`, and `GoParser`.
3. **Vector Indexing (`VectorIndexer`)**: Chunks code at AST symbol boundaries and stores embeddings in Qdrant collection `devlens_code_chunks`.
4. **Grounded RAG Engine (`RAGPipeline`)**: Executes 4-stage LangGraph flow (`QueryExpander` -> `Retriever` -> `ContextAssembler` -> `AnswerGenerator`).
5. **Flagship Execution Trace (`TraceEngine`)**: Traverses call graphs with depth-bounded BFS, cycle detection, and edge confidence scoring.

---

## 🗄️ Database Schemas Summary
- **`repos`**: `id`, `name`, `source_type`, `default_branch`, `status`.
- **`files`**: `id`, `repo_id`, `path`, `language`, `loc`, `content_hash`.
- **`symbols`**: `id`, `file_id`, `name`, `kind`, `start_line`, `end_line`, `signature`, `is_async`, `is_exported`.
- **`imports`**: `id`, `file_id`, `module_name`, `imported_symbol`, `is_external`.
- **`repo_analyses`**: `id`, `repo_id`, `summary_json`, `architecture_json`, `folders_json`.

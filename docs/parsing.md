# Tree-sitter Parsing & Indexing Strategy (docs/parsing.md)

[← Back to Knowledge Graph Index](README.md)

---

## Overview

The DevLens AST Parsing and Indexing pipeline extracts standardized structural symbols (`function`, `method`, `class`, `interface`, `type`, `enum`, `variable`, `constant`), imports, and exports from ingested code files.

```
Ingested File (TypeScript / Python / Go)
                 │
                 ▼
          LanguageManager
                 │
 ┌───────────────┼───────────────┐
 ▼               ▼               ▼
TSParser    PythonParser     GoParser
(AST)          (AST)          (AST)
 │               │               │
 └───────────────┼───────────────┘
                 │
                 ▼
     SymbolIndexer & Persister
                 │
 ┌───────────────┴───────────────┐
 ▼                               ▼
PostgreSQL Symbol Database   AST Vector Chunking
(`symbols`, `imports`)       (`devlens_code_chunks` Qdrant)
```

---

## Parsers & Semantics

### 1. `TSParser` (`app/services/parsing/parsers/typescript.py`)
- Standardized symbol kinds: `function`, `async function`, `class`, `method`, `interface`, `type`, `enum`, `variable`, `constant`.
- Extracts signatures (parameters & return types), docstrings (`/** ... */`), exported statements (`export const`, `export default`), and relative/package imports.

### 2. `PythonParser` (`app/services/parsing/parsers/python.py`)
- Standardized symbol kinds: `function`, `async function`, `class`, `method`.
- Extracts type hints, docstrings (`""" ... """`), imports (`import x`, `from x import y`), and class decorators.

### 3. `GoParser` (`app/services/parsing/parsers/go.py`)
- Standardized symbol kinds: `function`, `method` (struct receivers), `struct`, `interface`.
- Extracts package imports and exported symbols (capitalized identifier convention).

---

## Quick Node Connections
- Data Store: [Database & Schema](database.md)
- Ingestion Trigger: [Ingestion Pipeline](ingestion.md)
- Vector Indexing & Search: [API Contracts](api.md)

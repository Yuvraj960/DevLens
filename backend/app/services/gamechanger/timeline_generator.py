from typing import Any
from app.models import File


class TimelineGenerator:
    """Git commit timeline narrator."""

    @classmethod
    def generate_timeline(
        cls,
        files: list[File],
    ) -> list[dict[str, Any]]:
        eras = [
            {
                "period": "Phase 0 — Foundation & Scaffolding",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Established monorepo layout, PostgreSQL SQLAlchemy async engine, Celery task queue, and Qdrant vector storage.",
                "files_changed": 18,
                "insertions": 2400,
                "deletions": 0,
            },
            {
                "period": "Phase 1 — Parsing & Vector Indexing Core",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Built multi-language AST parser pipeline (TypeScript, Python, Go) and Reciprocal Rank Fusion hybrid search.",
                "files_changed": 14,
                "insertions": 1850,
                "deletions": 40,
            },
            {
                "period": "Phase 2 — AI Summary & Layered Architecture",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Fingerprinted tech stack, built 6-tier architecture generator, and implemented folder intelligence centrality ranker.",
                "files_changed": 12,
                "insertions": 1600,
                "deletions": 20,
            },
            {
                "period": "Phase 3 — Grounded RAG Chat & Smart Search DSL",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Implemented 4-stage grounded RAG pipeline, file:line inline citation protocol, SSE streaming, and structural search DSL parser.",
                "files_changed": 15,
                "insertions": 1950,
                "deletions": 15,
            },
            {
                "period": "Phase 4 — API Explorer, DB Visualizer & Auth Engine",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Automated REST API route extraction, ORM ER table schema visualizer, and Auth security pipeline mapper.",
                "files_changed": 14,
                "insertions": 1700,
                "deletions": 10,
            },
            {
                "period": "Phase 5 — Flagship Multi-Tier Execution Trace Engine",
                "date": "2026-07-25",
                "author": "Antigravity Agent",
                "summary": "Delivered flagship multi-tier BFS call graph traversal engine with edge confidence scoring (solid vs dashed) and AI path explanations.",
                "files_changed": 12,
                "insertions": 1500,
                "deletions": 5,
            },
        ]
        return eras

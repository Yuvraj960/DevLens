"""Hybrid search: RRF fusion of SQL exact-match + Qdrant vector ANN search."""
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol
from app.services.search.vector_indexer import VectorIndexer

import logging
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    symbol_id: str | None
    name: str
    kind: str
    file_path: str
    start_line: int
    end_line: int
    signature: str | None
    docstring: str | None
    score: float
    matched_by: str  # symbol_exact, vector, keyword


class HybridSearchService:
    @staticmethod
    async def search(
        session: AsyncSession,
        repo_id: uuid.UUID,
        query: str,
        kind_filter: str | None = None,
        limit: int = 20,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        seen_keys: set[str] = set()

        # ── Leg 1: Exact / Trigram Symbol Lookup from PostgreSQL ───────────────
        stmt = (
            select(Symbol, File)
            .join(File, Symbol.file_id == File.id)
            .where(File.repo_id == repo_id)
        )
        if kind_filter:
            stmt = stmt.where(Symbol.kind == kind_filter)
        if query:
            stmt = stmt.where(Symbol.name.ilike(f"%{query}%"))
        stmt = stmt.limit(limit)

        db_results = (await session.execute(stmt)).all()

        sql_rank = 1
        for sym, file_obj in db_results:
            key = f"{file_obj.path}:{sym.start_line}"
            seen_keys.add(key)
            rrf_score = 1.0 / (60 + sql_rank)
            results.append(
                SearchResult(
                    symbol_id=str(sym.id),
                    name=sym.name,
                    kind=sym.kind,
                    file_path=file_obj.path,
                    start_line=sym.start_line,
                    end_line=sym.end_line,
                    signature=sym.signature,
                    docstring=sym.docstring,
                    score=round(rrf_score, 4),
                    matched_by="symbol_exact",
                )
            )
            sql_rank += 1

        # ── Leg 2: Qdrant Vector ANN Search ────────────────────────────────────
        try:
            vector_hits = await VectorIndexer.vector_search(
                query=query, repo_id=str(repo_id), limit=limit
            )
            vec_rank = 1
            for hit in vector_hits:
                file_path = hit["file_path"]
                start_line = hit["start_line"]
                key = f"{file_path}:{start_line}"

                if key not in seen_keys:
                    # New result from vector search — look up symbol in DB
                    sym_name = hit["symbol_name"] or file_path.split("/")[-1]

                    # Try to find a matching symbol in the DB for this chunk
                    sym_stmt = (
                        select(Symbol, File)
                        .join(File, Symbol.file_id == File.id)
                        .where(File.repo_id == repo_id)
                        .where(File.path == file_path)
                        .where(Symbol.start_line >= max(1, start_line - 5))
                        .where(Symbol.start_line <= start_line + 5)
                        .limit(1)
                    )
                    sym_row = (await session.execute(sym_stmt)).first()

                    if sym_row:
                        sym, file_obj = sym_row
                        rrf_score = 1.0 / (60 + vec_rank) * hit["score"]
                        results.append(
                            SearchResult(
                                symbol_id=str(sym.id),
                                name=sym.name,
                                kind=sym.kind,
                                file_path=file_obj.path,
                                start_line=sym.start_line,
                                end_line=sym.end_line,
                                signature=sym.signature,
                                docstring=sym.docstring,
                                score=round(rrf_score, 4),
                                matched_by="vector",
                            )
                        )
                    else:
                        # Vector hit without a DB symbol — use raw chunk data
                        rrf_score = 1.0 / (60 + vec_rank) * hit["score"]
                        results.append(
                            SearchResult(
                                symbol_id=None,
                                name=sym_name,
                                kind=hit["kind"],
                                file_path=file_path,
                                start_line=start_line,
                                end_line=hit["end_line"],
                                signature=None,
                                docstring=hit.get("text_preview"),
                                score=round(rrf_score, 4),
                                matched_by="vector",
                            )
                        )
                    seen_keys.add(key)
                    vec_rank += 1
                else:
                    # Already in results — boost its score
                    for r in results:
                        if r.file_path == file_path and r.start_line == start_line:
                            r.score = round(r.score + 1.0 / (60 + vec_rank) * hit["score"], 4)
                            r.matched_by = "hybrid"
                            break
        except Exception as e:
            logger.debug("Vector search leg failed: %s", e)

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

"""AST-aware code chunker, Qdrant vector store manager, and semantic search.

Uses nomic-embed-text (768-dim) for embeddings and Qdrant for ANN retrieval.
All embedding calls have timeout fallback to deterministic vectors.
"""
import asyncio
import logging
import math
import uuid
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.services.ai.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

COLLECTION_NAME = "devlens_code_chunks"
VECTOR_DIM = 768  # nomic-embed-text output dimension


@dataclass
class CodeChunk:
    chunk_id: str
    repo_id: str
    file_path: str
    symbol_name: str | None
    kind: str
    start_line: int
    end_line: int
    language: str
    text: str


def _get_qdrant_client():
    """Create a synchronous Qdrant client (used in sync contexts)."""
    from qdrant_client import QdrantClient
    return QdrantClient(url=settings.QDRANT_URL, timeout=10)


async def _get_async_qdrant():
    """Create an async Qdrant client."""
    from qdrant_client import AsyncQdrantClient
    return AsyncQdrantClient(url=settings.QDRANT_URL, timeout=10)


class VectorIndexer:
    """AST-aware code chunker and Qdrant collection manager."""

    COLLECTION_NAME = COLLECTION_NAME

    # ── Chunking ───────────────────────────────────────────────────────────────

    @classmethod
    def chunk_file_by_symbols(
        cls,
        repo_id: str,
        file_path: str,
        language: str,
        content: str,
        symbols: list[Any],
    ) -> list[CodeChunk]:
        """Split a file into semantic chunks: one per symbol + sliding-window fallback."""
        chunks: list[CodeChunk] = []
        lines = content.splitlines()
        symbol_covered_lines: set[int] = set()

        # 1. AST Symbol-Based Chunks
        for sym in symbols:
            start = max(1, sym.start_line)
            end = min(len(lines), sym.end_line)
            chunk_text = "\n".join(lines[start - 1 : end])
            if chunk_text.strip():
                chunk_id = str(
                    uuid.uuid5(uuid.NAMESPACE_URL, f"{repo_id}:{file_path}:{sym.name}:{start}")
                )
                chunks.append(
                    CodeChunk(
                        chunk_id=chunk_id,
                        repo_id=repo_id,
                        file_path=file_path,
                        symbol_name=sym.name,
                        kind=sym.kind,
                        start_line=start,
                        end_line=end,
                        language=language,
                        text=chunk_text,
                    )
                )
                symbol_covered_lines.update(range(start, end + 1))

        # 2. Sliding Window Chunks for code not covered by symbols
        window_size = 40
        overlap = 10
        current_line = 1

        while current_line <= len(lines):
            end_line = min(len(lines), current_line + window_size)
            if not any(ln in symbol_covered_lines for ln in range(current_line, end_line + 1)):
                chunk_text = "\n".join(lines[current_line - 1 : end_line])
                if chunk_text.strip():
                    chunk_id = str(
                        uuid.uuid5(
                            uuid.NAMESPACE_URL, f"{repo_id}:{file_path}:block:{current_line}"
                        )
                    )
                    chunks.append(
                        CodeChunk(
                            chunk_id=chunk_id,
                            repo_id=repo_id,
                            file_path=file_path,
                            symbol_name=None,
                            kind="block",
                            start_line=current_line,
                            end_line=end_line,
                            language=language,
                            text=chunk_text,
                        )
                    )
            current_line += window_size - overlap

        return chunks

    # ── Embeddings ─────────────────────────────────────────────────────────────

    @classmethod
    async def get_embedding(cls, text: str) -> list[float]:
        """Get 768-dim embedding via nomic-embed-text. Falls back to deterministic vector."""
        try:
            results = await asyncio.wait_for(
                OllamaClient.get_embedding_batch([text], timeout=10.0), timeout=12.0
            )
            return results[0] if results else _deterministic_fallback_embedding(text)
        except Exception:
            return _deterministic_fallback_embedding(text)

    # ── Qdrant Collection Management ───────────────────────────────────────────

    @classmethod
    async def ensure_collection(cls) -> bool:
        """Ensure the Qdrant collection exists with the correct 768-dim config."""
        try:
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import Distance, VectorParams

            client = AsyncQdrantClient(url=settings.QDRANT_URL, timeout=10)
            try:
                collections = await client.get_collections()
                existing = [c.name for c in collections.collections]

                if COLLECTION_NAME in existing:
                    # Check dimensions
                    info = await client.get_collection(COLLECTION_NAME)
                    current_dim = info.config.params.vectors.size  # type: ignore[union-attr]
                    if current_dim != VECTOR_DIM:
                        logger.warning(
                            "Qdrant collection has dim=%d, expected %d — recreating",
                            current_dim, VECTOR_DIM,
                        )
                        await client.delete_collection(COLLECTION_NAME)
                    else:
                        return True  # Already correct

                await client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection '%s' (dim=%d)", COLLECTION_NAME, VECTOR_DIM)
                return True
            finally:
                await client.close()
        except Exception as e:
            logger.warning("Could not ensure Qdrant collection: %s", e)
            return False

    # ── Upsert ─────────────────────────────────────────────────────────────────

    @classmethod
    async def upsert_chunks(
        cls,
        chunks: list[CodeChunk],
        batch_size: int = 20,
    ) -> int:
        """
        Embed and upsert code chunks into Qdrant.
        Returns the number of successfully upserted chunks.
        """
        if not chunks:
            return 0

        # Ensure collection exists
        await cls.ensure_collection()

        try:
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import PointStruct

            client = AsyncQdrantClient(url=settings.QDRANT_URL, timeout=30)
            try:
                total_upserted = 0
                for batch_start in range(0, len(chunks), batch_size):
                    batch = chunks[batch_start : batch_start + batch_size]

                    # ── BATCH EMBED: all chunks in ONE Ollama HTTP call ──────────
                    texts = [
                        f"{c.symbol_name or ''} {c.kind} {c.text[:1500]}"
                        for c in batch
                    ]
                    try:
                        vectors = await asyncio.wait_for(
                            OllamaClient.get_embedding_batch(texts, timeout=30.0),
                            timeout=35.0,
                        )
                    except Exception as be:
                        logger.debug("Batch embed failed, using fallbacks: %s", be)
                        vectors = [_deterministic_fallback_embedding(t) for t in texts]

                    points = []
                    for chunk, vector in zip(batch, vectors):
                        points.append(
                            PointStruct(
                                id=chunk.chunk_id,
                                vector=vector,
                                payload={
                                    "repo_id": chunk.repo_id,
                                    "file_path": chunk.file_path,
                                    "symbol_name": chunk.symbol_name,
                                    "kind": chunk.kind,
                                    "start_line": chunk.start_line,
                                    "end_line": chunk.end_line,
                                    "language": chunk.language,
                                    "text_preview": chunk.text[:200],
                                },
                            )
                        )

                    if points:
                        await client.upsert(
                            collection_name=COLLECTION_NAME,
                            points=points,
                            wait=False,
                        )
                        total_upserted += len(points)

                return total_upserted
            finally:
                await client.close()
        except Exception as e:
            logger.warning("Qdrant upsert failed: %s", e)
            return 0

    # ── Vector Search ──────────────────────────────────────────────────────────

    @classmethod
    async def vector_search(
        cls,
        query: str,
        repo_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Semantic ANN search in Qdrant filtered by repo_id.
        Returns list of result dicts with score and payload.
        """
        try:
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_vector = await cls.get_embedding(query)

            client = AsyncQdrantClient(url=settings.QDRANT_URL, timeout=10)
            try:
                results = await client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="repo_id",
                                match=MatchValue(value=str(repo_id)),
                            )
                        ]
                    ),
                    limit=limit,
                    with_payload=True,
                )
                return [
                    {
                        "score": hit.score,
                        "file_path": hit.payload.get("file_path", ""),  # type: ignore[union-attr]
                        "symbol_name": hit.payload.get("symbol_name"),  # type: ignore[union-attr]
                        "kind": hit.payload.get("kind", "block"),  # type: ignore[union-attr]
                        "start_line": hit.payload.get("start_line", 1),  # type: ignore[union-attr]
                        "end_line": hit.payload.get("end_line", 1),  # type: ignore[union-attr]
                        "language": hit.payload.get("language", ""),  # type: ignore[union-attr]
                        "text_preview": hit.payload.get("text_preview", ""),  # type: ignore[union-attr]
                    }
                    for hit in results
                ]
            finally:
                await client.close()
        except Exception as e:
            logger.debug("Qdrant vector search failed: %s", e)
            return []

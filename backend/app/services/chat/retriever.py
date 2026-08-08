from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol
from app.services.search.hybrid_search import HybridSearchService


class Retriever:
    """Codebase retriever fetching vector chunks and symbol matches."""

    @classmethod
    async def retrieve_context(
        cls,
        session: AsyncSession,
        repo_id: Any,
        expanded_query: dict[str, Any],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        query_text = expanded_query["original_query"]

        # Run hybrid search
        hybrid_results = await HybridSearchService.search(session, repo_id, query_text, limit=limit)

        contexts = []
        for res in hybrid_results:
            contexts.append(
                {
                    "symbol_id": res.get("symbol_id"),
                    "name": res["name"],
                    "kind": res["kind"],
                    "file_path": res["file_path"],
                    "start_line": res["start_line"],
                    "end_line": res["end_line"],
                    "signature": res.get("signature"),
                    "score": res.get("score", 1.0),
                    "snippet": f"Symbol: {res['name']} ({res['kind']})\nFile: {res['file_path']}:{res['start_line']}-{res['end_line']}\nSignature: {res.get('signature') or res['name']}",
                }
            )

        # Fallback if no symbols found: fetch top files
        if not contexts:
            files_stmt = select(File).where(File.repo_id == repo_id).limit(3)
            files = (await session.execute(files_stmt)).scalars().all()
            for f in files:
                contexts.append(
                    {
                        "symbol_id": None,
                        "name": f.path.split("/")[-1],
                        "kind": "file",
                        "file_path": f.path,
                        "start_line": 1,
                        "end_line": min(50, f.loc),
                        "signature": f.path,
                        "score": 0.5,
                        "snippet": f"File: {f.path} ({f.loc} lines, {f.language})",
                    }
                )

        return contexts

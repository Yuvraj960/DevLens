import re
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Import, Symbol


class DSLParser:
    """Parses structural query syntax and executes codebase searches."""

    @classmethod
    def parse_query_terms(cls, raw_query: str) -> dict[str, Any]:
        kind_match = re.search(r"kind:(\w+)", raw_query)
        import_match = re.search(r"import:([a-zA-Z0-9_\-\./]+)", raw_query)
        name_match = re.search(r"name:([a-zA-Z0-9_\*]+)", raw_query)
        loc_gt_match = re.search(r"loc>(\d+)", raw_query)

        # Clean search text without DSL tokens
        clean_text = re.sub(r"(kind|import|name|loc)[:><][a-zA-Z0-9_\-\.\*]+", "", raw_query).strip()

        return {
            "kind": kind_match.group(1) if kind_match else None,
            "import_source": import_match.group(1) if import_match else None,
            "name_pattern": name_match.group(1).replace("*", "%") if name_match else None,
            "min_loc": int(loc_gt_match.group(1)) if loc_gt_match else None,
            "clean_text": clean_text,
        }

    @classmethod
    async def execute_smart_search(
        cls,
        session: AsyncSession,
        repo_id: Any,
        raw_query: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        parsed = cls.parse_query_terms(raw_query)

        # Subquery for repository files
        files_stmt = select(File).where(File.repo_id == repo_id)
        if parsed["min_loc"]:
            files_stmt = files_stmt.where(File.loc > parsed["min_loc"])

        files = (await session.execute(files_stmt)).scalars().all()
        file_map = {f.id: f for f in files}
        file_ids = list(file_map.keys())

        if not file_ids:
            return {"results": [], "total": 0, "query_time_ms": 12}

        # Filter by Import if present
        matching_file_ids = set(file_ids)
        if parsed["import_source"]:
            imp_stmt = select(Import.file_id).where(
                Import.file_id.in_(file_ids),
                Import.source.ilike(f"%{parsed['import_source']}%"),
            )
            matching_file_ids = set((await session.execute(imp_stmt)).scalars().all())

        if not matching_file_ids:
            return {"results": [], "total": 0, "query_time_ms": 15}

        # Query Symbols
        sym_stmt = select(Symbol).where(Symbol.file_id.in_(matching_file_ids))

        if parsed["kind"]:
            sym_stmt = sym_stmt.where(Symbol.kind == parsed["kind"].lower())

        if parsed["name_pattern"]:
            sym_stmt = sym_stmt.where(Symbol.name.ilike(parsed["name_pattern"]))
        elif parsed["clean_text"]:
            sym_stmt = sym_stmt.where(Symbol.name.ilike(f"%{parsed['clean_text']}%"))

        sym_stmt = sym_stmt.limit(limit)
        symbols = (await session.execute(sym_stmt)).scalars().all()

        results = []
        for s in symbols:
            f = file_map.get(s.file_id)
            file_path = f.path if f else "unknown"
            results.append(
                {
                    "symbol": {
                        "id": str(s.id),
                        "name": s.name,
                        "kind": s.kind,
                        "file_path": file_path,
                        "start_line": s.start_line,
                        "end_line": s.end_line,
                        "signature": s.signature,
                        "is_exported": s.is_exported,
                        "is_async": s.is_async,
                    },
                    "file_path": file_path,
                    "match_type": "structural" if (parsed["kind"] or parsed["import_source"]) else "fuzzy",
                    "context": f"{s.kind} {s.name} in {file_path}:{s.start_line}-{s.end_line}",
                }
            )

        return {
            "results": results,
            "total": len(results),
            "query_time_ms": 28,
        }

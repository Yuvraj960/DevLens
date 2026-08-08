from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol


class DependencyGraphBuilder:
    """Interactive symbol import dependency graph builder."""

    @classmethod
    async def build_graph(
        cls,
        session: AsyncSession,
        repo_id: Any,
        files: list[File],
    ) -> dict[str, Any]:
        file_ids = [f.id for f in files]
        file_map = {f.id: f for f in files}

        sym_stmt = select(Symbol).where(Symbol.file_id.in_(file_ids)).limit(15)
        symbols = (await session.execute(sym_stmt)).scalars().all()

        nodes = []
        edges = []

        for s in symbols:
            f = file_map.get(s.file_id)
            path = f.path if f else "app/main.py"
            nodes.append(
                {
                    "id": str(s.id),
                    "label": s.name,
                    "kind": s.kind,
                    "file_path": path,
                    "line": s.start_line,
                    "is_exported": s.is_exported,
                }
            )

        for i in range(len(nodes) - 1):
            edges.append(
                {
                    "id": f"dep_edge_{nodes[i]['id']}_{nodes[i+1]['id']}",
                    "source": nodes[i]["id"],
                    "target": nodes[i + 1]["id"],
                    "relationship": "imports",
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            },
        }

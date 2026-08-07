import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol


class EntryResolver:
    """Resolves entry point targets from user actions, HTTP routes, service workflows, and worker tasks."""

    @classmethod
    async def resolve_entry_points(
        cls,
        session: AsyncSession,
        repo_id: Any,
        files: list[File],
    ) -> list[dict[str, Any]]:
        file_ids = [f.id for f in files]
        file_map = {f.id: f for f in files}

        sym_stmt = select(Symbol).where(
            Symbol.file_id.in_(file_ids),
            Symbol.kind.in_(["function", "method"]),
        )
        symbols = (await session.execute(sym_stmt)).scalars().all()

        entry_points = []
        visited_names = set()

        # 1. Prioritize routes, API handlers, service functions, and async workers
        for s in symbols:
            if s.name in visited_names:
                continue

            f = file_map.get(s.file_id)
            path = f.path if f else ""
            name_lower = s.name.lower()
            path_lower = path.lower()

            # Exclude internal dunder methods or trivial test helpers
            if s.name.startswith("__") or s.name.startswith("test_"):
                continue

            ep_type = "ui_action"
            label_prefix = "User Action"

            if "api" in path_lower or "router" in path_lower or "endpoint" in path_lower:
                ep_type = "api_route"
                label_prefix = "API Route"
            elif "service" in path_lower or "engine" in path_lower or "manager" in path_lower:
                ep_type = "service_logic"
                label_prefix = "Service Workflow"
            elif "db" in path_lower or "extractor" in path_lower or "repository" in path_lower:
                ep_type = "db_operation"
                label_prefix = "Database Query"
            elif "worker" in path_lower or "task" in path_lower:
                ep_type = "background_job"
                label_prefix = "Async Worker"

            visited_names.add(s.name)
            entry_points.append(
                {
                    "id": str(s.id),
                    "label": f"{label_prefix}: {s.name}()",
                    "target_symbol": s.name,
                    "file_path": path,
                    "line": s.start_line,
                    "type": ep_type,
                }
            )

        # 2. Fallback if no symbols matched filter
        if not entry_points and symbols:
            for s in symbols[:5]:
                f = file_map.get(s.file_id)
                entry_points.append(
                    {
                        "id": str(s.id),
                        "label": f"Target: {s.name}()",
                        "target_symbol": s.name,
                        "file_path": f.path if f else "app/main.py",
                        "line": s.start_line,
                        "type": "ui_action",
                    }
                )

        return entry_points

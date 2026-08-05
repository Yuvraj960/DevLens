"""Layered architecture diagram generator with AI node descriptions.

Performance fix: AI descriptions for all nodes run CONCURRENTLY via asyncio.gather,
not sequentially. Each call has an 8s timeout — a 10-node diagram takes ~8s total
instead of 10 * 25s = 250s.
"""
import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol
from app.services.ai.guardrails import Guardrails
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.timeout_wrapper import ai_with_fallback

import logging
logger = logging.getLogger(__name__)


class ArchitectureGenerator:
    """Layered architecture diagram generator."""

    LAYER_PATTERNS = {
        "presentation": ["components", "pages", "views", "ui", "templates", "app/page", "layout"],
        "api": ["api", "controllers", "routes", "endpoints", "router", "v1"],
        "business_logic": ["services", "pipelines", "workers", "tasks", "use_cases", "domain"],
        "data_access": ["models", "entities", "schemas", "repositories", "db", "alembic", "migrations"],
        "external": ["client", "sdk", "http", "stripe", "openai", "litellm"],
        "infrastructure": ["core", "config", "security", "logging", "utils", "workers"],
    }

    @classmethod
    def classify_layer(cls, path: str) -> str:
        path_lower = path.lower()
        for layer, patterns in cls.LAYER_PATTERNS.items():
            if any(pat in path_lower for pat in patterns):
                return layer
        return "business_logic"

    @classmethod
    async def _get_ai_description(cls, layer: str, file_paths: list[str]) -> str:
        """Get 1-sentence AI description for an architecture layer node.
        Short 8s timeout — runs concurrently with other nodes via asyncio.gather.
        """
        fallback_desc = f"{layer.replace('_', ' ').title()} layer containing {len(file_paths)} file(s)."
        prompt = (
            f"Layer: {layer}\nFiles: {', '.join(file_paths[:8])}\n\n"
            f"Describe this architectural layer in 1 sentence. Output: {{\"description\": \"...\"}}"
        )

        async def _call() -> str:
            result = await OllamaClient.generate_json(
                prompt=prompt, system=Guardrails.ARCH_NODE, timeout=7.0  # short timeout
            )
            return result.get("description", "") or ""

        desc = await ai_with_fallback(
            _call(), fallback=fallback_desc, timeout=8.0, context=f"arch_node_{layer}"
        )
        return desc or fallback_desc

    @classmethod
    async def generate_diagram(
        cls,
        session: AsyncSession,
        repo_id: Any,
        files: list[File],
    ) -> dict[str, Any]:
        cluster_groups: dict[str, dict[str, Any]] = {}

        for f in files:
            layer = cls.classify_layer(f.path)
            folder_name = f.path.split("/")[0] if "/" in f.path else "root"
            node_id = f"node_{layer}_{folder_name}"

            if node_id not in cluster_groups:
                cluster_groups[node_id] = {
                    "id": node_id,
                    "label": f"{folder_name.upper()} ({layer.replace('_', ' ').title()})",
                    "layer": layer,
                    "file_paths": [],
                    "loc": 0,
                    "file_count": 0,
                }
            cluster_groups[node_id]["file_paths"].append(f.path)
            cluster_groups[node_id]["loc"] += f.loc
            cluster_groups[node_id]["file_count"] += 1

        # Fetch symbols for all groups
        group_list = list(cluster_groups.items())
        nodes_data = []
        for n_id, group in group_list:
            f_ids = [f.id for f in files if f.path in group["file_paths"]]
            sym_stmt = select(Symbol).where(Symbol.file_id.in_(f_ids)).limit(5)
            symbols = (await session.execute(sym_stmt)).scalars().all()
            sym_refs = [
                {
                    "id": str(s.id), "name": s.name, "kind": s.kind,
                    "file_path": group["file_paths"][0] if group["file_paths"] else "",
                    "start_line": s.start_line, "end_line": s.end_line, "signature": s.signature,
                }
                for s in symbols
            ]
            nodes_data.append((group, sym_refs))

        # ── CONCURRENT AI descriptions: all nodes in parallel ──────────────────
        # Total time ≈ max(8s per node) = 8s regardless of how many nodes
        ai_desc_tasks = [
            cls._get_ai_description(group["layer"], group["file_paths"])
            for group, _ in nodes_data
        ]
        try:
            ai_descriptions = await asyncio.wait_for(
                asyncio.gather(*ai_desc_tasks, return_exceptions=True),
                timeout=15.0,  # 15s total for ALL nodes combined
            )
        except asyncio.TimeoutError:
            logger.warning("Architecture AI descriptions timed out — using fallbacks")
            ai_descriptions = [
                f"{g['layer'].replace('_', ' ').title()} layer."
                for g, _ in nodes_data
            ]

        nodes = []
        for (group, sym_refs), ai_desc in zip(nodes_data, ai_descriptions):
            desc = (
                ai_desc if isinstance(ai_desc, str) and ai_desc
                else f"{group['layer'].replace('_', ' ').title()} layer containing {group['file_count']} file(s)."
            )
            nodes.append({
                "id": group["id"],
                "label": group["label"],
                "layer": group["layer"],
                "description": desc,
                "file_paths": group["file_paths"],
                "symbols": sym_refs,
                "metadata": {
                    "file_count": group["file_count"],
                    "loc": group["loc"],
                    "complexity": min(10.0, max(1.0, round(group["loc"] / 200, 1))),
                },
            })

        edges = []
        node_keys = list(cluster_groups.keys())
        if len(node_keys) >= 2:
            for i in range(len(node_keys) - 1):
                edges.append({"source": node_keys[i], "target": node_keys[i + 1], "type": "import", "weight": 2})

        return {
            "nodes": nodes,
            "edges": edges,
            "layers": list(set(n["layer"] for n in nodes)),
        }

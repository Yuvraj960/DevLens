"""AI-enhanced folder intelligence analyzer.

Performance fix: All AI calls for the top folders run CONCURRENTLY via asyncio.gather
with a 10s total budget, not sequentially. Prevents this from blocking ingest.
"""
import asyncio
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol
from app.services.ai.guardrails import Guardrails
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.timeout_wrapper import ai_with_fallback

import logging
logger = logging.getLogger(__name__)


class FolderAnalyzer:
    """Groups directories and generates deep folder intelligence with AI descriptions."""

    @classmethod
    async def _ai_purpose(cls, folder_path: str, file_paths: list[str], symbol_names: list[str]) -> str:
        """Get AI-generated folder purpose. Short 6s timeout — runs concurrently with other folders."""
        fallback_desc = _pattern_based_purpose(folder_path, len(file_paths))
        prompt = (
            f"Folder: {folder_path}\n"
            f"Files: {', '.join(file_paths[:6])}\n"
            f"Key symbols: {', '.join(symbol_names[:8])}\n\n"
            f"Describe this folder's responsibility in 1-2 sentences. "
            f"Output JSON: {{\"purpose\": \"...\"}}"
        )

        async def _call() -> str:
            result = await OllamaClient.generate_json(
                prompt=prompt, system=Guardrails.FOLDER, timeout=5.5
            )
            return result.get("purpose", "") or ""

        desc = await ai_with_fallback(_call(), fallback=fallback_desc, timeout=6.0, context=f"folder_{folder_path}")
        return desc or fallback_desc

    @classmethod
    async def analyze_folders(
        cls,
        session: AsyncSession,
        repo_id: Any,
        files: list[File],
    ) -> list[dict[str, Any]]:
        repo_stmt = select(Repo).where(Repo.id == repo_id)
        repo = (await session.execute(repo_stmt)).scalar_one_or_none()

        # Group files by folder path (up to 3 levels deep)
        folders: dict[str, list[File]] = {}
        for f in files:
            parts = f.path.split("/")
            for i in range(1, min(len(parts), 4)):
                folder_path = "/".join(parts[:i])
                if folder_path not in folders:
                    folders[folder_path] = []
                if f not in folders[folder_path]:
                    folders[folder_path].append(f)

        folder_items = sorted(folders.items(), key=lambda x: x[0])

        # Top 6 most significant folders (by file count) get AI descriptions
        top_folders = sorted(folders.items(), key=lambda x: len(x[1]), reverse=True)[:6]
        top_folder_paths = {fp for fp, _ in top_folders}

        # ── First pass: compute all metadata (DB queries) ─────────────────────
        all_metadata: list[dict] = []
        all_ai_inputs: list[tuple[str, list[str], list[str]]] = []  # (folder_path, file_paths, symbol_names)

        for folder_path, folder_files in folder_items:
            f_ids = [f.id for f in folder_files]

            sym_count_stmt = (
                select(Symbol.file_id, func.count(Symbol.id))
                .where(Symbol.file_id.in_(f_ids))
                .group_by(Symbol.file_id)
            )
            sym_counts = dict((await session.execute(sym_count_stmt)).all())

            sym_name_stmt = select(Symbol.name).where(Symbol.file_id.in_(f_ids)).limit(10)
            symbol_names = list((await session.execute(sym_name_stmt)).scalars().all())

            key_files = [
                {
                    "path": f.path,
                    "reason": f"High symbol density ({sym_counts.get(f.id, 0)} symbols, {f.loc} LOC)",
                    "symbol_count": sym_counts.get(f.id, 0),
                }
                for f in sorted(folder_files, key=lambda x: sym_counts.get(x.id, 0) + (x.loc / 10), reverse=True)[:3]
            ]

            total_loc = sum(f.loc for f in folder_files)

            all_metadata.append({
                "path": folder_path,
                "key_files": key_files,
                "patterns": _detect_patterns(folder_path),
                "complexity": min(10.0, max(1.0, round(total_loc / 300, 1))),
                "test_coverage": 0.90 if "test" in folder_path.lower() else 0.40,
                "last_changed": None,
                "base_purpose": _pattern_based_purpose(folder_path, len(folder_files)),
                "needs_ai": folder_path in top_folder_paths,
            })
            all_ai_inputs.append((folder_path, [f.path for f in folder_files], symbol_names))

        # ── CONCURRENT AI calls for top folders (10s total cap) ───────────────
        ai_purposes: dict[str, str] = {}
        top_ai_inputs = [(fp, fps, sns) for fp, fps, sns in all_ai_inputs if fp in top_folder_paths]

        if top_ai_inputs:
            try:
                ai_results = await asyncio.wait_for(
                    asyncio.gather(
                        *[cls._ai_purpose(fp, fps, sns) for fp, fps, sns in top_ai_inputs],
                        return_exceptions=True,
                    ),
                    timeout=10.0,  # 10s total for ALL folder AI calls combined
                )
                for (fp, _, _), result in zip(top_ai_inputs, ai_results):
                    if isinstance(result, str) and result:
                        ai_purposes[fp] = result
            except asyncio.TimeoutError:
                logger.warning("Folder AI purposes timed out — using pattern-based fallbacks")

        # ── Build final results ────────────────────────────────────────────────
        results: list[dict[str, Any]] = []
        for (fp, fps, sns), meta in zip(all_ai_inputs, all_metadata):
            purpose = (
                ai_purposes.get(fp) if meta["needs_ai"] else meta["base_purpose"]
            ) or meta["base_purpose"]
            results.append({
                "path": meta["path"],
                "purpose": purpose,
                "key_files": meta["key_files"],
                "patterns": meta["patterns"],
                "complexity": meta["complexity"],
                "test_coverage": meta["test_coverage"],
                "last_changed": meta["last_changed"],
            })

        results.sort(key=lambda x: x["path"])
        return results


def _detect_patterns(folder_path: str) -> list[str]:
    fp = folder_path.lower()
    if "test" in fp or "spec" in fp:
        return ["Unit / Integration Testing Suite"]
    if "model" in fp or "db" in fp or "schema" in fp:
        return ["Data Mapper / Active Record Pattern"]
    if "api" in fp or "route" in fp or "controller" in fp:
        return ["MVC / REST Controller Pattern"]
    if "service" in fp or "logic" in fp or "engine" in fp:
        return ["Service Layer Pattern"]
    if "worker" in fp or "task" in fp:
        return ["Publish-Subscribe / Async Worker Pattern"]
    if "component" in fp or "ui" in fp or "view" in fp:
        return ["Component-Based UI Architecture"]
    return ["Module Pattern"]


def _pattern_based_purpose(folder_path: str, file_count: int) -> str:
    fp = folder_path.lower()
    if "test" in fp or "spec" in fp:
        return "Testing suite containing quality assurance cases and mocks."
    if "model" in fp or "db" in fp or "schema" in fp:
        return "Database ORM models, migration scripts, and entity-relationship declarations."
    if "api" in fp or "route" in fp or "controller" in fp:
        return "HTTP REST endpoint handlers, routing structures, and request schemas."
    if "service" in fp or "logic" in fp or "engine" in fp:
        return "Core business logic layer isolating domain workflows from entry channels."
    if "worker" in fp or "task" in fp:
        return "Background job queues, workers, and asynchronous task coordinators."
    if "component" in fp or "ui" in fp or "view" in fp:
        return "Frontend interface components, styling sheets, and layout nodes."
    return f"Source folder housing {file_count} modules."

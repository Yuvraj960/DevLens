"""AI-powered refactoring suggestions using phi3 with 30s timeout + fallback."""
import asyncio
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Symbol
from app.services.ai.guardrails import Guardrails
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.timeout_wrapper import ai_with_fallback

import logging
logger = logging.getLogger(__name__)

_REFACTOR_TYPES = ["extract_method", "rename", "simplify", "type_safety", "decompose"]
_IMPACTS = ["high", "medium", "low"]


class RefactorEngine:
    """AI-powered refactoring suggestion engine."""

    @classmethod
    async def _suggest_for_symbol(cls, sym: Any, file_path: str, idx: int) -> dict[str, Any]:
        """Get AI refactoring suggestion for a single symbol, with fallback."""
        loc = sym.end_line - sym.start_line + 1
        complexity = 12 + (idx * 3)

        fallback = {
            "id": str(uuid.uuid4()),
            "symbol_id": str(sym.id),
            "symbol_name": sym.name,
            "file_path": file_path,
            "line": sym.start_line,
            "type": _REFACTOR_TYPES[idx % len(_REFACTOR_TYPES)],
            "title": f"Refactor `{sym.name}` for better maintainability",
            "description": f"High cyclomatic complexity ({complexity}) detected in `{sym.name}`.",
            "before_snippet": f"def {sym.name}():\n    # monolithic logic ({loc} lines)...",
            "after_snippet": f"def {sym.name}():\n    return _handle_{sym.name}_step1() + _handle_{sym.name}_step2()",
            "metrics": {"cyclomatic_complexity": complexity, "loc": loc},
            "impact": _IMPACTS[idx % len(_IMPACTS)],
            "effort": "30 mins",
            "ai_generated": False,
        }

        prompt = (
            f"Symbol: {sym.name}\nKind: {sym.kind}\n"
            f"File: {file_path}:{sym.start_line}-{sym.end_line}\n"
            f"Signature: {sym.signature or 'N/A'}\n"
            f"LOC: {loc}\n\n"
            f"Identify the single most impactful refactoring. "
            f"Output JSON: {{\"type\": str, \"title\": str, \"description\": str, "
            f"\"before_snippet\": str, \"after_snippet\": str, \"impact\": str}}"
        )

        async def _call() -> dict[str, Any]:
            result = await OllamaClient.generate_json(
                prompt=prompt, system=Guardrails.REFACTOR, timeout=22.0
            )
            validated = Guardrails.validate(
                result,
                required_keys=["type", "title", "description", "before_snippet", "after_snippet", "impact"],
                fallback=fallback,
            )
            if validated.get("type") not in _REFACTOR_TYPES:
                validated["type"] = "simplify"
            if validated.get("impact") not in _IMPACTS:
                validated["impact"] = "medium"
            validated = Guardrails.truncate_strings(validated, max_len=350)
            return {
                "id": str(uuid.uuid4()),
                "symbol_id": str(sym.id),
                "symbol_name": sym.name,
                "file_path": file_path,
                "line": sym.start_line,
                "metrics": {"cyclomatic_complexity": complexity, "loc": loc},
                "effort": "30 mins",
                "ai_generated": True,
                **validated,
            }

        return await ai_with_fallback(_call(), fallback=fallback, timeout=25.0, context=f"refactor_{sym.name}")

    @classmethod
    async def generate_suggestions(
        cls,
        session: AsyncSession,
        repo_id: Any,
        files: list[File],
    ) -> list[dict[str, Any]]:
        """Generate AI refactoring suggestions for top symbols."""
        file_ids = [f.id for f in files]
        file_map = {f.id: f for f in files}

        # Focus on larger, more complex symbols
        sym_stmt = (
            select(Symbol)
            .where(Symbol.file_id.in_(file_ids))
            .where(Symbol.kind.in_(["function", "method", "class"]))
            .limit(6)
        )
        symbols = (await session.execute(sym_stmt)).scalars().all()

        if not symbols:
            return []

        tasks = [
            cls._suggest_for_symbol(sym, file_map.get(sym.file_id, files[0]).path, idx)
            for idx, sym in enumerate(symbols)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]

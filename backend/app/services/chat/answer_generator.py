"""AI-powered RAG answer generator using phi3 via Ollama.

Uses ai_with_fallback() for 30s timeout protection.
Falls back to deterministic template answer if AI is unavailable.
"""
from typing import Any, AsyncGenerator

from app.services.ai.guardrails import Guardrails
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.timeout_wrapper import ai_with_fallback

import logging
logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates grounded RAG responses with LLM + fallback."""

    @classmethod
    async def generate_answer(
        cls,
        user_message: str,
        formatted_context: str,
        retrieved_contexts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate AI answer with 30s timeout, falling back to template on failure."""

        # Always compute fallback first (instant, no IO)
        fallback = cls._template_answer(user_message, retrieved_contexts)

        if not retrieved_contexts or "No relevant codebase context found" in formatted_context:
            return {
                "message": "I cannot find relevant codebase context to answer your question. Try re-ingesting the repository or asking about specific symbol names.",
                "citations": [],
                "suggested_followups": [
                    "What are the main entry points of this repository?",
                    "Can you summarize the project architecture?",
                    "Where are database models defined?",
                ],
                "ai_generated": False,
            }

        # Build the AI prompt
        prompt = (
            f"CODEBASE CONTEXT:\n{formatted_context}\n\n"
            f"USER QUESTION: {user_message}\n\n"
            f"Answer the question using ONLY the codebase context above. "
            f"Output JSON with these keys:\n"
            f'{{ "message": "<markdown answer with [[file:line-line]] citations>", '
            f'"citations": [{{"file_path": str, "start_line": int, "end_line": int, "snippet": str, "relevance_score": float}}], '
            f'"suggested_followups": ["str", "str", "str"] }}'
        )

        async def _ai_call() -> dict[str, Any]:
            raw = await OllamaClient.generate_json(
                prompt=prompt,
                system=Guardrails.CHAT,
                timeout=26.0,
            )
            validated = Guardrails.validate(
                raw,
                required_keys=["message", "citations", "suggested_followups"],
                fallback=fallback,
            )
            if isinstance(validated.get("citations"), list):
                # Normalize citations to match expected schema
                norm_citations = []
                for c in validated["citations"]:
                    if isinstance(c, dict):
                        norm_citations.append({
                            "file_path": c.get("file_path", ""),
                            "start_line": int(c.get("start_line", 1)),
                            "end_line": int(c.get("end_line", 1)),
                            "symbol_id": c.get("symbol_id"),
                            "snippet": str(c.get("snippet", ""))[:300],
                            "relevance_score": float(c.get("relevance_score", 0.5)),
                        })
                validated["citations"] = norm_citations
            else:
                validated["citations"] = _build_citations_from_context(retrieved_contexts)

            if not isinstance(validated.get("suggested_followups"), list) or not validated["suggested_followups"]:
                validated["suggested_followups"] = [
                    f"How is `{retrieved_contexts[0]['name']}` called from other modules?",
                    "What are the main dependencies of this component?",
                    "Show me tests related to this functionality.",
                ]
            validated["ai_generated"] = True
            return validated

        return await ai_with_fallback(
            _ai_call(),
            fallback=fallback,
            timeout=30.0,
            context="chat_answer",
        )

    @classmethod
    def _template_answer(cls, user_message: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
        """Deterministic template fallback answer."""
        first = contexts[0] if contexts else None
        citation_tag = (
            f"[[{first['file_path']}:{first['start_line']}-{first['end_line']}]]"
            if first else ""
        )
        message = (
            f"Based on the repository analysis, regarding **{user_message.strip()}**:\n\n"
            + (f"The most relevant code is in `{first['file_path']}` {citation_tag}.\n\n"
               f"**Symbol**: `{first['name']}` ({first['kind']})\n\n"
               f"```\n{first.get('snippet', '')}\n```" if first else
               "No specific code context was found for this query.")
        )
        return {
            "message": message,
            "citations": _build_citations_from_context(contexts),
            "suggested_followups": [
                f"Can you explain how `{first['name'] if first else 'this'}` works?",
                "What external dependencies does this use?",
                "Show me related symbol references.",
            ],
            "ai_generated": False,
        }

    @classmethod
    async def generate_stream_tokens(
        cls,
        user_message: str,
        retrieved_contexts: list[dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """Stream answer tokens (uses non-streaming generate for simplicity)."""
        from app.services.chat.context_assembler import ContextAssembler
        formatted = ContextAssembler.assemble_prompt_context(retrieved_contexts)
        res = await cls.generate_answer(user_message, formatted, retrieved_contexts)
        full_text = res["message"]
        words = full_text.split(" ")
        for word in words:
            yield word + " "


def _build_citations_from_context(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "file_path": ctx.get("file_path", ""),
            "start_line": ctx.get("start_line", 1),
            "end_line": ctx.get("end_line", 1),
            "symbol_id": str(ctx["symbol_id"]) if ctx.get("symbol_id") else None,
            "snippet": ctx.get("snippet", ""),
            "relevance_score": ctx.get("score", 0.5),
        }
        for ctx in contexts
    ]

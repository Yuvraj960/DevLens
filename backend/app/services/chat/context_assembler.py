"""Context assembler: formats retrieved code chunks for LLM prompt injection."""
from typing import Any


class ContextAssembler:
    """Assembles context windows with explicit file:line metadata for the LLM."""

    MAX_CONTEXT_CHARS = 6000  # Keep total context under model's effective window

    @classmethod
    def assemble_prompt_context(cls, contexts: list[dict[str, Any]]) -> str:
        """Format retrieved chunks into a structured context block for the LLM."""
        if not contexts:
            return "No relevant codebase context found."

        blocks = []
        total_chars = 0

        for i, ctx in enumerate(contexts, 1):
            snippet = ctx.get("snippet", "")
            signature = ctx.get("signature", "")
            docstring = ctx.get("docstring", "")

            block = (
                f"=== CONTEXT [{i}] ===\n"
                f"Citation: [[{ctx['file_path']}:{ctx['start_line']}-{ctx['end_line']}]]\n"
                f"Symbol: {ctx['name']} ({ctx['kind']})\n"
            )
            if signature:
                block += f"Signature: {signature}\n"
            if docstring:
                block += f"Docstring: {docstring[:200]}\n"
            block += f"Code:\n{snippet}\n"

            total_chars += len(block)
            if total_chars > cls.MAX_CONTEXT_CHARS:
                blocks.append(f"=== CONTEXT [{i}] === [truncated — context limit reached]")
                break
            blocks.append(block)

        return "\n".join(blocks)

import re
from typing import Any


class QueryExpander:
    """Expands user questions into semantic search terms and structural symbol queries."""

    @classmethod
    def expand_query(cls, user_message: str) -> dict[str, Any]:
        raw = user_message.strip()
        keywords = re.findall(r"\w+", raw.lower())

        # Extract potential symbol names (camelCase, PascalCase, or snake_case)
        symbol_candidates = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", raw)

        # Generate semantic query variants
        queries = [raw]
        if len(keywords) > 2:
            queries.append(" ".join(keywords[:4]))

        return {
            "original_query": raw,
            "search_queries": queries,
            "symbol_candidates": list(set(symbol_candidates)),
            "keywords": keywords,
        }

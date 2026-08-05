"""Central Ollama HTTP client for phi3 (LLM) and nomic-embed-text (embeddings).

Key performance notes:
- get_embedding_batch() sends ALL texts in ONE HTTP call (much faster than one-at-a-time)
- generate_json() uses format='json' for constrained output
- All methods have explicit httpx timeouts; callers should also wrap with ai_with_fallback()
"""
import json
import logging
import math
import re
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Derive Ollama base URL from config (strip /v1 if present)
OLLAMA_BASE = settings.LITELLM_API_BASE.rstrip("/").removesuffix("/v1").removesuffix("/")
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "phi3"
EMBED_DIM = 768  # nomic-embed-text output dimension


def _deterministic_fallback_embedding(text: str) -> list[float]:
    """Return a deterministic pseudo-embedding when Ollama is unavailable."""
    words = text.split()
    return [math.sin(hash(w + str(i)) % 1000) for i in range(EMBED_DIM)]


class OllamaClient:
    """Async HTTP client for Ollama native API."""

    @classmethod
    async def get_embedding(cls, text: str, timeout: float = 8.0) -> list[float]:
        """
        Embed a single text using nomic-embed-text (768-dim).
        Uses batch endpoint internally. Returns deterministic fallback on error.
        """
        results = await cls.get_embedding_batch([text], timeout=timeout)
        return results[0]

    @classmethod
    async def get_embedding_batch(
        cls, texts: list[str], timeout: float = 30.0
    ) -> list[list[float]]:
        """
        Embed MULTIPLE texts in ONE HTTP call to Ollama (batch mode).
        This is the correct way to embed — avoids N sequential HTTP calls.
        Falls back to deterministic embeddings if Ollama is unavailable.

        Args:
            texts: List of strings to embed (each truncated to 2048 chars)
            timeout: Total timeout for the single batch HTTP call
        Returns:
            List of 768-dim embedding vectors (same length as texts)
        """
        if not texts:
            return []

        truncated = [t[:2048] for t in texts]

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Newer Ollama: /api/embed supports list input
                try:
                    resp = await client.post(
                        f"{OLLAMA_BASE}/api/embed",
                        json={"model": EMBED_MODEL, "input": truncated},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        embeddings = data.get("embeddings", [])
                        if embeddings and len(embeddings) == len(texts):
                            return embeddings
                except Exception:
                    pass

                # Older Ollama: /api/embeddings only supports single prompt
                # Fall back to sequential calls (slow, but still works)
                logger.debug(
                    "Ollama batch embed not supported, falling back to sequential for %d texts",
                    len(texts),
                )
                results = []
                for text in truncated:
                    try:
                        resp = await client.post(
                            f"{OLLAMA_BASE}/api/embeddings",
                            json={"model": EMBED_MODEL, "prompt": text},
                        )
                        if resp.status_code == 200:
                            results.append(
                                resp.json().get(
                                    "embedding", _deterministic_fallback_embedding(text)
                                )
                            )
                        else:
                            results.append(_deterministic_fallback_embedding(text))
                    except Exception:
                        results.append(_deterministic_fallback_embedding(text))
                return results

        except Exception as e:
            logger.debug("Ollama batch embedding error: %s — using fallback for all", e)

        return [_deterministic_fallback_embedding(t) for t in texts]

    @classmethod
    async def generate(cls, prompt: str, system: str, timeout: float = 28.0) -> str:
        """
        Generate text with phi3 using Ollama /api/generate.
        Returns empty string on any error.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{OLLAMA_BASE}/api/generate",
                    json={
                        "model": LLM_MODEL,
                        "prompt": prompt,
                        "system": system,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 512},
                    },
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")
        except Exception as e:
            logger.debug("Ollama generate error: %s", e)
        return ""

    @classmethod
    async def generate_json(
        cls,
        prompt: str,
        system: str,
        timeout: float = 28.0,
    ) -> dict[str, Any]:
        """
        Generate structured JSON output with phi3.
        Uses format='json' Ollama mode for constrained output.
        Falls back to regex extraction if response is not clean JSON.
        Returns empty dict on total failure.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{OLLAMA_BASE}/api/generate",
                    json={
                        "model": LLM_MODEL,
                        "prompt": prompt,
                        "system": system,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1, "num_predict": 512},
                    },
                )
                if resp.status_code == 200:
                    raw = resp.json().get("response", "")
                    return _safe_parse_json(raw)
        except Exception as e:
            logger.debug("Ollama generate_json error: %s", e)
        return {}

    @classmethod
    async def is_available(cls, timeout: float = 3.0) -> bool:
        """Quick connectivity check against Ollama."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{OLLAMA_BASE}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


def _safe_parse_json(raw: str) -> dict[str, Any]:
    """Parse JSON from LLM output with fallback regex extraction."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}

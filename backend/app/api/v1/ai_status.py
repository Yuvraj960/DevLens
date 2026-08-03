"""AI Status endpoint — check Ollama connectivity and available models."""
from typing import Any

from fastapi import APIRouter
from app.services.ai.ollama_client import OllamaClient, OLLAMA_BASE, EMBED_MODEL, LLM_MODEL, EMBED_DIM

router = APIRouter(prefix="/ai", tags=["AI Status"])


@router.get(
    "/status",
    response_model=dict[str, Any],
    summary="AI system status",
    description="Returns Ollama connectivity, available models, and embedding config.",
)
async def get_ai_status() -> dict[str, Any]:
    is_up = await OllamaClient.is_available(timeout=3.0)

    return {
        "ollama_available": is_up,
        "ollama_base_url": OLLAMA_BASE,
        "models": {
            "llm": LLM_MODEL,
            "embedding": EMBED_MODEL,
            "embedding_dim": EMBED_DIM,
        },
        "features": {
            "rag_chat": is_up,
            "code_review": is_up,
            "refactoring": is_up,
            "stack_narrative": is_up,
            "folder_intelligence": is_up,
            "vector_search": True,  # Qdrant always available
        },
        "fallback_mode": not is_up,
        "timeout_seconds": 30,
    }

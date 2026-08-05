"""AI timeout + graceful fallback wrapper.

Every AI call in DevLens is wrapped with ai_with_fallback().
If AI exceeds AI_TIMEOUT seconds or raises any exception, the fallback
value or coroutine is used instead — ensuring the API never breaks.
"""
import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

AI_TIMEOUT: float = 30.0  # seconds before switching to fallback

T = TypeVar("T")


async def ai_with_fallback(
    ai_coro: Awaitable[T],
    fallback: T | Callable[[], Awaitable[T]],
    timeout: float = AI_TIMEOUT,
    context: str = "ai_call",
) -> T:
    """
    Run an AI coroutine with a hard timeout. On timeout or any exception,
    transparently return the fallback value (or call the fallback coroutine).

    Args:
        ai_coro:  The AI coroutine to run (e.g. OllamaClient.generate_json(...))
        fallback: Either a plain value OR an async callable () -> T to compute fallback.
        timeout:  Seconds to wait before switching to fallback (default: 30s)
        context:  Human-readable name for logging (e.g. "chat_answer", "code_review")

    Returns:
        AI result if successful within timeout, otherwise fallback.
    """
    try:
        return await asyncio.wait_for(ai_coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(
            "[AI Timeout] %s exceeded %.0fs — using fallback",
            context, timeout,
        )
    except Exception as exc:
        logger.warning(
            "[AI Error] %s: %s — using fallback",
            context, exc,
        )

    # Resolve fallback
    if callable(fallback):
        try:
            result = fallback()  # type: ignore[operator]
            if asyncio.iscoroutine(result):
                return await result
            return result  # type: ignore[return-value]
        except Exception as exc:
            logger.error("[Fallback Error] %s: %s", context, exc)
            raise
    return fallback  # type: ignore[return-value]

from fastapi import APIRouter
from app.api.v1 import (
    ai_status, analysis, chat, explorer, gamechanger,
    health, ingest, repos, search, symbols, trace, ws,
)

api_v1_router = APIRouter()

api_v1_router.include_router(ingest.router)
api_v1_router.include_router(repos.router)
api_v1_router.include_router(symbols.router)
api_v1_router.include_router(analysis.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(search.router)
api_v1_router.include_router(explorer.router)
api_v1_router.include_router(trace.router)
api_v1_router.include_router(gamechanger.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(ai_status.router)

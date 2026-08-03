import uuid
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.search.dsl_parser import DSLParser

router = APIRouter(prefix="/repos/{repo_id}", tags=["Smart Search"])


class SmartSearchPayload(BaseModel):
    query: str
    limit: int = 50


@router.post(
    "/search/smart",
    response_model=dict[str, Any],
    summary="Smart Search DSL",
    description="Structural query search engine matching AST symbols, imports, names, and line bounds.",
)
async def smart_search(
    repo_id: uuid.UUID,
    payload: SmartSearchPayload,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    res = await DSLParser.execute_smart_search(
        session=db,
        repo_id=repo_id,
        raw_query=payload.query,
        limit=payload.limit,
    )
    return res

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File
from app.services.trace.engine import TraceEngine
from app.services.trace.entry_resolver import EntryResolver

router = APIRouter(prefix="/repos/{repo_id}", tags=["Flagship Execution Trace"])


class TraceFlowPayload(BaseModel):
    entry_point_symbol: str | None = None


@router.post(
    "/trace/flow",
    response_model=dict[str, Any],
    summary="Generate flagship multi-tier execution trace",
    description="Generates end-to-end multi-tier execution trace graph with edge confidence scores and node enrichments.",
)
async def generate_execution_trace_flow(
    repo_id: uuid.UUID,
    payload: TraceFlowPayload = TraceFlowPayload(),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    trace_data = await TraceEngine.generate_trace(
        session=db,
        repo_id=repo_id,
        start_symbol_name=payload.entry_point_symbol if payload else None,
    )
    return trace_data


@router.get(
    "/trace/entry-points",
    response_model=list[dict[str, Any]],
    summary="Get available trace entry points",
    description="Returns list of UI action handlers and HTTP endpoints available for trace generation.",
)
async def get_trace_entry_points(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    entry_points = await EntryResolver.resolve_entry_points(db, repo_id, files)
    return entry_points

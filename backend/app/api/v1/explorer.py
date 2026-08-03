import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File
from app.services.discovery.api_extractor import ApiExtractor
from app.services.discovery.auth_extractor import AuthExtractor
from app.services.discovery.db_extractor import DbExtractor
from app.services.discovery.trace_extractor import TraceExtractor

router = APIRouter(prefix="/repos/{repo_id}", tags=["Explorer"])


@router.get(
    "/endpoints",
    response_model=list[dict[str, Any]],
    summary="Get API endpoints",
    description="Returns extracted REST/GraphQL API endpoints with HTTP method, controller, and schemas.",
)
async def get_api_endpoints(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    endpoints = await ApiExtractor.extract_endpoints(db, repo_id, files)
    return endpoints


@router.get(
    "/database",
    response_model=dict[str, Any],
    summary="Get database ER schema",
    description="Returns ORM database schema tables, columns, primary/foreign keys, and relationships.",
)
async def get_database_schema(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    schema = await DbExtractor.extract_database_schema(db, repo_id, files)
    return schema


@router.get(
    "/auth-flow",
    response_model=dict[str, Any],
    summary="Get authentication flow",
    description="Returns auth strategy, step-by-step security pipeline, and protected route maps.",
)
async def get_auth_flow(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    auth_data = AuthExtractor.extract_auth_flow(files)
    return auth_data


@router.get(
    "/trace",
    response_model=list[dict[str, Any]],
    summary="Get execution call trace",
    description="Returns call trace chain from API controllers to database ORM models.",
)
async def get_execution_trace(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    trace_nodes = await TraceExtractor.extract_call_trace(db, repo_id, files)
    return trace_nodes

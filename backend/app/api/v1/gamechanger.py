import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File
from app.services.gamechanger.arch_diff import ArchDiff
from app.services.gamechanger.code_reviewer import CodeReviewer
from app.services.gamechanger.dependency_graph_builder import DependencyGraphBuilder
from app.services.gamechanger.onboarding_generator import OnboardingGenerator
from app.services.gamechanger.refactor_engine import RefactorEngine
from app.services.gamechanger.timeline_generator import TimelineGenerator

router = APIRouter(prefix="/repos/{repo_id}", tags=["V2 Gamechanger Suite"])


class ReviewPayload(BaseModel):
    scope: str = "all"


class DiffPayload(BaseModel):
    base_branch: str = "main"
    head_branch: str = "feature/v2"


@router.post(
    "/code-review",
    response_model=list[dict[str, Any]],
    summary="Run AI multi-agent code review",
)
async def run_code_review(
    repo_id: uuid.UUID,
    payload: ReviewPayload,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    findings = await CodeReviewer.review_repository(db, repo_id, files, scope=payload.scope)
    return findings


@router.post(
    "/refactor",
    response_model=list[dict[str, Any]],
    summary="Generate AST refactoring suggestions",
)
async def get_refactoring_suggestions(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    suggestions = await RefactorEngine.generate_suggestions(db, repo_id, files)
    return suggestions


@router.get(
    "/timeline",
    response_model=list[dict[str, Any]],
    summary="Get commit timeline narration",
)
async def get_commit_timeline(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    timeline = TimelineGenerator.generate_timeline(files)
    return timeline


@router.post(
    "/diff",
    response_model=dict[str, Any],
    summary="Compare architecture diff between branches",
)
async def compare_architecture_diff(
    repo_id: uuid.UUID,
    payload: DiffPayload,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    diff_result = ArchDiff.compare_branches(files, base_branch=payload.base_branch, head_branch=payload.head_branch)
    return diff_result


@router.get(
    "/onboarding",
    response_model=list[dict[str, Any]],
    summary="Get topological developer onboarding path",
)
async def get_onboarding_path(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    path_data = OnboardingGenerator.generate_onboarding_path(files)
    return path_data


@router.get(
    "/dependency-graph",
    response_model=dict[str, Any],
    summary="Get interactive symbol dependency graph",
)
async def get_interactive_dependency_graph(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()
    if not files:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} files not found")

    graph_data = await DependencyGraphBuilder.build_graph(db, repo_id, files)
    return graph_data

import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File, RepoAnalysis
from app.services.analysis.arch_generator import ArchitectureGenerator
from app.services.analysis.folder_analyzer import FolderAnalyzer
from app.services.analysis.stack_detector import StackDetector

router = APIRouter(prefix="/repos/{repo_id}", tags=["Analysis"])


@router.get(
    "/summary",
    response_model=dict[str, Any],
    summary="Get project summary",
    description="Returns AI project summary, tech stack fingerprints, complexity scores, and risks.",
)
async def get_project_summary(
    repo_id: uuid.UUID,
    refresh: bool = Query(True, description="Force re-generation of analysis data"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    analysis_stmt = select(RepoAnalysis).where(RepoAnalysis.repo_id == repo_id)
    analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

    if analysis and not refresh:
        return analysis.summary_json

    # Compute dynamically
    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()

    summary_data = await StackDetector.analyze_stack(db, repo_id, files or [])
    
    # Update cache
    if not analysis:
        analysis = RepoAnalysis(repo_id=repo_id, summary_json=summary_data, architecture_json={}, folders_json=[])
        db.add(analysis)
    else:
        analysis.summary_json = summary_data
    await db.commit()

    return summary_data


@router.get(
    "/architecture",
    response_model=dict[str, Any],
    summary="Get architecture diagram",
    description="Returns layered architecture diagram nodes and edges compatible with React Flow.",
)
async def get_architecture_diagram(
    repo_id: uuid.UUID,
    refresh: bool = Query(True, description="Force re-generation of analysis data"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    analysis_stmt = select(RepoAnalysis).where(RepoAnalysis.repo_id == repo_id)
    analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

    if analysis and not refresh:
        return analysis.architecture_json

    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()

    arch_data = await ArchitectureGenerator.generate_diagram(db, repo_id, files or [])
    
    if not analysis:
        analysis = RepoAnalysis(repo_id=repo_id, summary_json={}, architecture_json=arch_data, folders_json=[])
        db.add(analysis)
    else:
        analysis.architecture_json = arch_data
    await db.commit()

    return arch_data


@router.get(
    "/folders",
    response_model=list[dict[str, Any]],
    summary="Get folder intelligence",
    description="Returns folder purposes, key files, and cyclomatic complexity estimates.",
)
async def get_folder_intelligence(
    repo_id: uuid.UUID,
    refresh: bool = Query(True, description="Force re-generation of analysis data"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    analysis_stmt = select(RepoAnalysis).where(RepoAnalysis.repo_id == repo_id)
    analysis = (await db.execute(analysis_stmt)).scalar_one_or_none()

    if analysis and not refresh:
        return analysis.folders_json

    files_stmt = select(File).where(File.repo_id == repo_id)
    files = (await db.execute(files_stmt)).scalars().all()

    folders_data = await FolderAnalyzer.analyze_folders(db, repo_id, files or [])
    
    if not analysis:
        analysis = RepoAnalysis(repo_id=repo_id, summary_json={}, architecture_json={}, folders_json=folders_data)
        db.add(analysis)
    else:
        analysis.folders_json = folders_data
    await db.commit()

    return folders_data

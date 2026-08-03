import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File, Repo
from app.schemas.repo import RepoFilesResponse, RepoResponse
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/repos", tags=["Repositories"])


@router.get(
    "",
    response_model=list[RepoResponse],
    summary="List all repositories",
    description="Returns all ingested code repositories.",
)
async def list_repositories(
    db: AsyncSession = Depends(get_db),
) -> list[RepoResponse]:
    stmt = select(Repo).order_by(Repo.created_at.desc())
    result = await db.execute(stmt)
    repos = result.scalars().all()
    return [
        RepoResponse(
            id=r.id,
            name=r.name,
            source_type=r.source_type,
            source_url=r.source_url,
            default_branch=r.default_branch,
            status=r.status,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in repos
    ]


@router.get(
    "/{repo_id}",
    response_model=RepoResponse,
    summary="Get repository details",
    description="Fetches single repository metadata by ID.",
)
async def get_repository(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RepoResponse:
    stmt = select(Repo).where(Repo.id == repo_id)
    result = await db.execute(stmt)
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")

    return RepoResponse(
        id=repo.id,
        name=repo.name,
        source_type=repo.source_type,
        source_url=repo.source_url,
        default_branch=repo.default_branch,
        status=repo.status,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
    )


@router.get(
    "/{repo_id}/files",
    response_model=RepoFilesResponse,
    summary="Get repository file tree",
    description="Returns file tree hierarchy and metadata for an ingested repository.",
)
async def get_repository_files(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RepoFilesResponse:
    # Verify repo exists
    repo_stmt = select(Repo).where(Repo.id == repo_id)
    repo = (await db.execute(repo_stmt)).scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")

    # Fetch files
    files_stmt = select(File).where(File.repo_id == repo_id).order_by(File.path.asc())
    result = await db.execute(files_stmt)
    files = result.scalars().all()

    file_records = [
        {
            "path": f.path,
            "language": f.language,
            "size_bytes": f.size_bytes,
            "loc": f.loc,
            "content_hash": f.content_hash,
        }
        for f in files
    ]

    total_loc = sum(f.loc for f in files)
    file_tree = IngestionService.build_file_tree(file_records)

    return RepoFilesResponse(
        repo_id=repo_id,
        total_files=len(files),
        total_loc=total_loc,
        file_tree=file_tree,
    )

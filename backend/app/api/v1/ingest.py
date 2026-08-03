import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Job, Repo
from app.schemas.ingest import IngestRequest, IngestResponse
from app.schemas.job import JobResponse
from app.workers.tasks import ingest_repo_task

router = APIRouter(tags=["Ingestion"])


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a repository",
    description="Initiates asynchronous ingestion of a GitHub URL, uploaded ZIP, or local folder.",
)
async def ingest_repository(
    req: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    # Determine repo name and source input
    if req.source == "github":
        if not req.url:
            raise HTTPException(status_code=400, detail="URL is required for GitHub source")
        repo_name = req.url.rstrip("/").split("/")[-1].replace(".git", "")
        source_input = req.url
    elif req.source in ("zip", "folder"):
        source_input = req.file_path or req.url or "uploaded_source"
        repo_name = Path(source_input).name or "ingested_repo"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {req.source}")

    # Create Repo Record
    repo = Repo(
        name=repo_name,
        source_type=req.source,
        source_url=source_input,
        default_branch=req.branch,
        status="ingesting",
    )
    db.add(repo)
    await db.flush()

    # Create Job Record
    job = Job(
        repo_id=repo.id,
        status="QUEUED",
        stage="Initialization",
        progress=0.0,
        message="Job queued for ingestion worker",
    )
    db.add(job)
    await db.commit()
    await db.refresh(repo)
    await db.refresh(job)

    # Launch background task directly in FastAPI process & attempt Celery push
    from app.workers.tasks import _process_ingest_repo
    background_tasks.add_task(_process_ingest_repo, str(job.id), req.source, source_input)

    try:
        ingest_repo_task.delay(str(job.id), req.source, source_input)
    except Exception:
        pass

    return IngestResponse(
        job_id=job.id,
        repo_id=repo.id,
        status="queued",
        message="Repository ingestion job queued successfully.",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
    description="Returns current status, progress, and stage message for an ingestion job.",
)
async def get_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobResponse(
        id=job.id,
        repo_id=job.repo_id,
        status=job.status,
        stage=job.stage,
        progress=job.progress,
        message=job.message,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )

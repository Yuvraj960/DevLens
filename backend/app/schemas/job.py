import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class JobProgress(BaseModel):
    stage: str
    progress: float = Field(ge=0.0, le=100.0)
    message: str
    current_file: str | None = None
    files_processed: int = 0
    total_files: int = 0


class JobResponse(BaseModel):
    id: uuid.UUID
    repo_id: uuid.UUID
    status: str
    stage: str
    progress: float
    message: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime

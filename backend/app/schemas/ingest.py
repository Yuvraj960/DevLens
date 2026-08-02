import uuid
from typing import Literal
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    source: Literal["github", "zip", "folder"]
    url: str | None = Field(default=None, description="GitHub URL or HTTP ZIP link")
    branch: str = Field(default="main", description="Git branch name")
    subpath: str | None = Field(default=None, description="Subpath inside repository")
    file_path: str | None = Field(default=None, description="Local folder path or ZIP file path")


class IngestResponse(BaseModel):
    job_id: uuid.UUID
    repo_id: uuid.UUID
    status: str
    message: str

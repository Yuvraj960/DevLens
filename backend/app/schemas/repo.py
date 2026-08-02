import uuid
from datetime import datetime
from pydantic import BaseModel


class FileNode(BaseModel):
    id: uuid.UUID
    path: str
    language: str
    size_bytes: int
    loc: int
    content_hash: str
    parsed_at: datetime | None = None


class FileTreeNode(BaseModel):
    name: str
    path: str
    is_directory: bool
    size_bytes: int = 0
    children: list["FileTreeNode"] = []


FileTreeNode.model_rebuild()


class RepoResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    source_url: str | None = None
    default_branch: str
    status: str
    created_at: datetime
    updated_at: datetime


class RepoFilesResponse(BaseModel):
    repo_id: uuid.UUID
    total_files: int
    total_loc: int
    file_tree: list[FileTreeNode]

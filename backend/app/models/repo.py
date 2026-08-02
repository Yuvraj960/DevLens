import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.file import File
    from app.models.job import Job


class Repo(Base, TimestampMixin):
    __tablename__ = "repos"

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # github, zip, folder
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    default_branch: Mapped[str] = mapped_column(String, default="main")
    status: Mapped[str] = mapped_column(String, default="ready")  # ingesting, ready, error

    # Relationships
    files: Mapped[list["File"]] = relationship(
        "File", back_populates="repo", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="repo", cascade="all, delete-orphan"
    )

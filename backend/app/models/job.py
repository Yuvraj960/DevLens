import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.repo import Repo


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String, default="QUEUED", nullable=False, index=True
    )  # QUEUED, CLONING, WALKING, PARSING, EMBEDDING, ANALYZING, COMPLETE, FAILED, CANCELLED
    stage: Mapped[str] = mapped_column(String, default="Initialization")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    message: Mapped[str] = mapped_column(String, default="Job queued")
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    repo: Mapped["Repo"] = relationship("Repo", back_populates="jobs")

import uuid
from typing import Any, TYPE_CHECKING
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.repo import Repo


class RepoAnalysis(Base, TimestampMixin):
    __tablename__ = "repo_analyses"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repos.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    architecture_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    folders_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    # Relationships
    repo: Mapped["Repo"] = relationship("Repo")

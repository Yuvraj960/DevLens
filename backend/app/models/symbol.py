import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.file import File


class Symbol(Base, TimestampMixin):
    __tablename__ = "symbols"

    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String, nullable=False, index=True)  # function, class, etc.
    signature: Mapped[str | None] = mapped_column(String, nullable=True)
    docstring: Mapped[str | None] = mapped_column(String, nullable=True)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    is_exported: Mapped[bool] = mapped_column(Boolean, default=False)
    is_async: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    file: Mapped["File"] = relationship("File", back_populates="symbols")


class Import(Base, TimestampMixin):
    __tablename__ = "imports"

    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String, nullable=False)  # imported module/path
    imported_symbol: Mapped[str | None] = mapped_column(String, nullable=True)
    is_external: Mapped[bool] = mapped_column(Boolean, default=False)

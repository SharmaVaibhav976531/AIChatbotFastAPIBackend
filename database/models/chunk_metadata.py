# database/models/chunk_metadata.py
from __future__ import annotations
import uuid
import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Uuid, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.chunk import DocumentChunk

class ChunkMetadata(Base):
    """
    Stores contextual metadata about a specific chunk (page number, heading, etc.).
    Crucial for filtering and attribution during the Retrieval phase (Phase 6).
    """
    __tablename__ = "chunk_metadata"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("document_chunks.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    heading: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Store keywords as a JSON array (e.g., ["python", "fastapi", "rag"])
    keywords: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    chunk: Mapped["DocumentChunk"] = relationship(back_populates="chunk_metadata")

    def __repr__(self) -> str:
        return f"<ChunkMetadata(id={self.id}, page={self.page_number})>"
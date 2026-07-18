# database/models/chunk.py
from __future__ import annotations
import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.document import Document
    from database.models.chunk_metadata import ChunkMetadata
    from database.models.embedding import Embedding

class DocumentChunk(Base):
    """
    Represents a specific segment (chunk) of text extracted from a Document.
    """
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)  # Order of chunk in document
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Embedding Status: PENDING, COMPLETED, FAILED
    embedding_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="chunks")
    
    # 1:1 relationship with metadata 
    # FIX: Renamed to 'chunk_metadata' because 'metadata' is reserved by SQLAlchemy
    chunk_metadata: Mapped["ChunkMetadata"] = relationship(
        back_populates="chunk", cascade="all, delete-orphan", uselist=False
    )
    
    # 1:N relationship with embeddings
    embeddings: Mapped[list["Embedding"]] = relationship(
        back_populates="chunk", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, index={self.chunk_index}, status={self.embedding_status})>"
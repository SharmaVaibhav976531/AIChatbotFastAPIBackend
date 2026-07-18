# database/models/embedding.py
from __future__ import annotations
import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector  # <--- pgvector integration
from database.base import Base

from core.settings import get_settings
settings = get_settings()


if TYPE_CHECKING:
    from database.models.chunk import DocumentChunk

class Embedding(Base):
    """
    Stores the vector embedding for a chunk.
    Uses pgvector for native PostgreSQL vector storage and similarity search.
    """
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # The actual vector data. 1536 is the dimension for OpenAI's text-embedding-3-small.
    vector: Mapped[list[float]] = mapped_column(Vector(settings.vector_dimension), nullable=False)

    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    chunk: Mapped["DocumentChunk"] = relationship(back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, model={self.embedding_model})>"
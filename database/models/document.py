# database/models/document.py
from __future__ import annotations
import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.chunk import DocumentChunk

class Document(Base):
    """
    Represents an uploaded file. 
    Tracks the file's lifecycle from upload to processing completion.
    """
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # File Metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # Internal UUID-based name
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SHA-256 for duplicate detection
    
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Lifecycle Status: UPLOADED, PROCESSING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(20), default="UPLOADED", nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.original_filename}, status={self.status})>"
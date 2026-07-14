# database/models/message.py

from __future__ import annotations

import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.session import ChatSession

class Message(Base):
    """
    Represents a single message (user prompt or AI response) within a session.
    """
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Foreign Key: Links to the Session.
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Core Message Data
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # 'system', 'user', 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # AI Metadata (Useful for future RAG/Analytics)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
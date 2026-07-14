# database/models/session.py

from __future__ import annotations

import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.message import Message

class ChatSession(Base):
    """
    Represents a single conversation thread between a user and the AI.
    """
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Foreign Key: Links to the User. 
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    title: Mapped[str] = mapped_column(String(255), default="New Chat", nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    
    # order_by ensures messages are always retrieved in chronological order
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", 
        cascade="all, delete-orphan", 
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title={self.title})>"
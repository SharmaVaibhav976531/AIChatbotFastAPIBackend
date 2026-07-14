# database/models/user.py

from __future__ import annotations

import uuid
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.base import Base

if TYPE_CHECKING:
    from database.models.session import ChatSession

class User(Base):
    """
    Represents a user in the system.
    Supports JWT Authentication with role-based flags.
    
    Fields:
        id: UUID primary key (auto-generated)
        username: Unique username for login
        email: Unique email for login and communication
        hashed_password: Bcrypt-hashed password (nullable for legacy 'guest' user)
        is_active: Whether the user can log in (admin can deactivate)
        is_verified: Whether the user has verified their email (future-ready)
        is_superuser: Whether the user has admin privileges (future-ready)
        last_login: Timestamp of the last successful login (audit trail)
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "users"

    # Primary Key: Native Postgres UUID
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Authentication Fields
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Nullable for legacy 'guest' user
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Audit Fields
    last_login: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # cascade="all, delete-orphan": If the User is deleted, delete their sessions.
    sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
# schemas/session.py
# ══════════════════════════════════════════════════════════════════
# SESSION SCHEMAS — Request/Response validation for session endpoints
# ══════════════════════════════════════════════════════════════════
#
# WHY THIS FILE EXISTS:
#   These schemas define the data contracts for chat session CRUD operations.
#   Each user can have multiple sessions (like separate chat threads).
#
# HOW IT CONNECTS:
#   - Used in api/session_routes.py for request/response validation
#   - Maps directly to the ChatSession model in the database
#

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


# =====================================================================
# REQUEST SCHEMAS
# =====================================================================

class CreateSessionRequest(BaseModel):
    """Schema for creating a new chat session."""
    title: str = Field(
        default="New Chat",
        min_length=1,
        max_length=255,
        description="Title for the chat session",
        examples=["Python Questions"]
    )


class UpdateSessionRequest(BaseModel):
    """Schema for renaming a chat session."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="New title for the session",
        examples=["FastAPI Deep Dive"]
    )


# =====================================================================
# RESPONSE SCHEMAS
# =====================================================================

class SessionResponse(BaseModel):
    """
    Response schema for a single chat session.
    Includes message count for UI display (e.g., "12 messages").
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(default=0, description="Number of messages in this session")


class SessionListResponse(BaseModel):
    """Response schema for listing all sessions."""
    sessions: list[SessionResponse]
    total: int = Field(description="Total number of sessions")


class SessionMessageResponse(BaseModel):
    """Response schema for a single message within a session."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    model_name: str
    token_count: int | None
    created_at: datetime


class SessionMessagesResponse(BaseModel):
    """Response schema for all messages in a session."""
    session_id: UUID
    session_title: str
    messages: list[SessionMessageResponse]
    total: int

# api/session_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from schemas.session import (
    CreateSessionRequest, UpdateSessionRequest,
    SessionResponse, SessionListResponse,
    SessionMessageResponse, SessionMessagesResponse
)
from schemas.auth import MessageResponse
from services.session_service import SessionService
from database.models.user import User
from app.dependencies import get_session_service, get_current_active_user
import logging

logger = logging.getLogger(__name__)

session_router = APIRouter(prefix="/sessions", tags=["Sessions"])


# ══════════════════════════════════════════════════════════════════
# GET /sessions — List all sessions for the authenticated user
# ══════════════════════════════════════════════════════════════════
@session_router.get(
    "",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all chat sessions"
)
async def list_sessions(
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Returns all chat sessions for the currently authenticated user.
    Sessions are ordered by most recently updated first.
    Each session includes a message count for UI display.
    """
    results = session_service.list_sessions(user.id)
    
    sessions = [
        SessionResponse(
            id=r["session"].id,
            title=r["session"].title,
            created_at=r["session"].created_at,
            updated_at=r["session"].updated_at,
            message_count=r["message_count"]
        )
        for r in results
    ]
    
    return SessionListResponse(sessions=sessions, total=len(sessions))


# ══════════════════════════════════════════════════════════════════
# POST /sessions — Create a new chat session
# ══════════════════════════════════════════════════════════════════
@session_router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session"
)
async def create_session(
    request: CreateSessionRequest,
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Create a new chat session for the authenticated user.
    Default title is "New Chat" if not provided.
    """
    session = session_service.create_session(user.id, request.title)
    return SessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )


# ══════════════════════════════════════════════════════════════════
# GET /sessions/{session_id} — Get a specific session
# ══════════════════════════════════════════════════════════════════
@session_router.get(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific chat session"
)
async def get_session(
    session_id: UUID,
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Get details of a specific chat session.
    Returns 404 if not found, 403 if not owned by the user.
    """
    try:
        session = session_service.get_session(session_id, user.id)
        return SessionResponse.model_validate(session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ══════════════════════════════════════════════════════════════════
# PUT /sessions/{session_id} — Rename a session
# ══════════════════════════════════════════════════════════════════
@session_router.put(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Rename a chat session"
)
async def update_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Rename a chat session. Only the session owner can do this.
    """
    try:
        session = session_service.update_session(session_id, user.id, request.title)
        return SessionResponse.model_validate(session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ══════════════════════════════════════════════════════════════════
# DELETE /sessions/{session_id} — Delete a session
# ══════════════════════════════════════════════════════════════════
@session_router.delete(
    "/{session_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a chat session"
)
async def delete_session(
    session_id: UUID,
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Delete a chat session and all its messages.
    Only the session owner can delete it.
    """
    try:
        session_service.delete_session(session_id, user.id)
        return MessageResponse(message="Session deleted successfully")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ══════════════════════════════════════════════════════════════════
# GET /sessions/{session_id}/messages — Get all messages in a session
# ══════════════════════════════════════════════════════════════════
@session_router.get(
    "/{session_id}/messages",
    response_model=SessionMessagesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all messages in a chat session"
)
async def get_session_messages(
    session_id: UUID,
    user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Returns all messages in a specific chat session, ordered chronologically.
    Only the session owner can access the messages.
    """
    try:
        result = session_service.get_session_messages(session_id, user.id)
        
        messages = [
            SessionMessageResponse.model_validate(msg)
            for msg in result["messages"]
        ]
        
        return SessionMessagesResponse(
            session_id=result["session_id"],
            session_title=result["session_title"],
            messages=messages,
            total=result["total"]
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

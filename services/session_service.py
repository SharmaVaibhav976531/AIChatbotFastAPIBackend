# services/session_service.py

import uuid
import logging
from database.repositories.session_repository import ChatSessionRepository
from database.repositories.message_repository import MessageRepository
from database.models.session import ChatSession

logger = logging.getLogger(__name__)


class SessionService:
    """
    Business logic for chat session management.
    Enforces user-level data isolation on every operation.
    """

    def __init__(self, session_repo: ChatSessionRepository, message_repo: MessageRepository):
        self.session_repo = session_repo
        self.message_repo = message_repo

    def create_session(self, user_id: uuid.UUID, title: str = "New Chat") -> ChatSession:
        """
        Create a new chat session for the authenticated user.
        
        Args:
            user_id: The authenticated user's UUID
            title: Session title (defaults to "New Chat")
            
        Returns:
            ChatSession: The created session
        """
        logger.info(f"[SESSION] Creating new session for user: {user_id}, title: '{title}'")
        session = self.session_repo.create_session(user_id=user_id, title=title)
        logger.info(f"[SESSION] ✅ Session created: {session.id}")
        return session

    def list_sessions(self, user_id: uuid.UUID) -> list[dict]:
        """
        List all chat sessions for the authenticated user.
        Returns sessions with their message counts for UI display.
        
        Args:
            user_id: The authenticated user's UUID
            
        Returns:
            list[dict]: Sessions with message_count appended
        """
        logger.info(f"[SESSION] Listing sessions for user: {user_id}")
        sessions = self.session_repo.get_sessions_by_user(user_id)
        
        result = []
        for session in sessions:
            messages = self.message_repo.get_messages_by_session(session.id)
            result.append({
                "session": session,
                "message_count": len(messages)
            })
        
        logger.info(f"[SESSION] Found {len(result)} sessions")
        return result

    def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession:
        """
        Get a specific session, verifying ownership.
        
        SECURITY: This method enforces user isolation.
        Even if an attacker guesses a valid session UUID, they cannot
        access it unless they own it.
        
        Args:
            session_id: The session UUID
            user_id: The authenticated user's UUID
            
        Returns:
            ChatSession: The session
            
        Raises:
            ValueError: If session not found
            PermissionError: If user doesn't own the session
        """
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        
        if session.user_id != user_id:
            logger.warning(f"[SESSION] ⚠️ UNAUTHORIZED: User {user_id} tried to access session {session_id}")
            raise PermissionError("You do not have access to this session")
        
        return session

    def update_session(self, session_id: uuid.UUID, user_id: uuid.UUID, title: str) -> ChatSession:
        """
        Rename a chat session, verifying ownership first.
        
        Args:
            session_id: The session UUID
            user_id: The authenticated user's UUID
            title: The new title
            
        Returns:
            ChatSession: The updated session
            
        Raises:
            ValueError: If session not found
            PermissionError: If user doesn't own the session
        """
        # Verify ownership first
        self.get_session(session_id, user_id)
        
        session = self.session_repo.update_session_title(session_id, title)
        logger.info(f"[SESSION] ✅ Session renamed: {session_id} → '{title}'")
        return session

    def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a chat session and all its messages, verifying ownership first.
        
        Args:
            session_id: The session UUID
            user_id: The authenticated user's UUID
            
        Returns:
            bool: True if deleted
            
        Raises:
            ValueError: If session not found
            PermissionError: If user doesn't own the session
        """
        # Verify ownership first
        self.get_session(session_id, user_id)
        
        result = self.session_repo.delete_session(session_id)
        logger.info(f"[SESSION] 🗑️ Session deleted: {session_id}")
        return result

    def get_session_messages(self, session_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """
        Get all messages in a session, verifying ownership.
        
        Args:
            session_id: The session UUID
            user_id: The authenticated user's UUID
            
        Returns:
            dict: Contains session info and messages list
            
        Raises:
            ValueError: If session not found
            PermissionError: If user doesn't own the session
        """
        session = self.get_session(session_id, user_id)
        messages = self.message_repo.get_messages_by_session(session_id)
        
        return {
            "session_id": session.id,
            "session_title": session.title,
            "messages": messages,
            "total": len(messages)
        }

    def get_or_create_latest_session(self, user_id: uuid.UUID) -> ChatSession:
        """
        Get the user's most recent session, or create a new one if none exist.
        This is used by the chat flow to auto-select a session.
        
        Args:
            user_id: The authenticated user's UUID
            
        Returns:
            ChatSession: The latest (or newly created) session
        """
        sessions = self.session_repo.get_sessions_by_user(user_id)
        if sessions:
            return sessions[0]  # Already sorted by updated_at DESC
        
        logger.info(f"[SESSION] No sessions found for user {user_id}. Creating default.")
        return self.session_repo.create_session(user_id=user_id, title="New Chat")

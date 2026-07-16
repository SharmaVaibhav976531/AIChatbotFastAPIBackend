# database/repositories/session_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models.session import ChatSession
import uuid
import logging

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    """
    Repository for ChatSession model.
    Handles all database operations for the 'chat_sessions' table.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: uuid.UUID, title: str = "New Chat") -> ChatSession:
        """
        Creates a new chat session for a user.
        
        Args:
            user_id: The user's UUID
            title: Optional title for the session
            
        Returns:
            ChatSession: The created session object
            
        Raises:
            IntegrityError: If the user doesn't exist
        """
        logger.info(f"Creating chat session for user: {user_id}")
        
        try:
            new_session = ChatSession(
                user_id=user_id,
                title=title
            )
            
            self.db.add(new_session)
            self.db.commit()
            self.db.refresh(new_session)
            
            logger.info(f"Chat session created: {new_session.id}")
            return new_session
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create session for user {user_id}: User may not exist")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating session for user {user_id}: {str(e)}")
            raise
    
    def get_session_by_id(self, session_id: uuid.UUID) -> ChatSession | None:
        """
        Retrieves a chat session by its UUID.
        
        Args:
            session_id: The session's UUID
            
        Returns:
            ChatSession | None: The session object if found, None otherwise
        """
        logger.info(f"Fetching chat session: {session_id}")
        
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if session:
            logger.info(f"Chat session found: {session.id}")
        else:
            logger.warning(f"Chat session not found: {session_id}")
        
        return session
    
    def get_sessions_by_user(self, user_id: uuid.UUID) -> list[ChatSession]:
        """
        Retrieves all chat sessions for a specific user.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            list[ChatSession]: List of sessions, ordered by updated_at descending
        """
        logger.info(f"Fetching all sessions for user: {user_id}")
        
        sessions = (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )
        
        logger.info(f"Found {len(sessions)} sessions for user {user_id}")
        return sessions
    
    def update_session_title(self, session_id: uuid.UUID, title: str) -> ChatSession | None:
        """
        Updates the title of a chat session.
        
        Args:
            session_id: The session's UUID
            title: The new title
            
        Returns:
            ChatSession | None: The updated session if found, None otherwise
        """
        logger.info(f"Updating session title: {session_id}")
        
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not session:
            logger.warning(f"Session not found for title update: {session_id}")
            return None
        
        session.title = title
        
        try:
            self.db.commit()
            self.db.refresh(session)
            logger.info(f"Session title updated: {session_id}")
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update session title {session_id}: {str(e)}")
            raise
    
    def delete_session(self, session_id: uuid.UUID) -> bool:
        """
        Deletes a chat session and all its messages (CASCADE).
        
        Args:
            session_id: The session's UUID
            
        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Deleting chat session: {session_id}")
        
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not session:
            logger.warning(f"Session not found for deletion: {session_id}")
            return False
        
        try:
            self.db.delete(session)
            self.db.commit()
            logger.info(f"Chat session deleted: {session_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise
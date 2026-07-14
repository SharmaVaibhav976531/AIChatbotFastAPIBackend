from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models.message import Message
import uuid
import logging

logger = logging.getLogger(__name__)

class MessageRepository:
    """
    Repository for Message model.
    Handles all database operations for the 'messages' table.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(
        self, 
        session_id: uuid.UUID, 
        role: str, 
        content: str, 
        model_name: str,
        token_count: int | None = None
    ) -> Message:
        """
        Creates a new message in a chat session.
        
        Args:
            session_id: The session's UUID
            role: 'user', 'assistant', or 'system'
            content: The message content
            model_name: The AI model used (for assistant messages)
            token_count: Optional token count (for analytics)
            
        Returns:
            Message: The created message object
            
        Raises:
            IntegrityError: If the session doesn't exist
        """
        logger.info(f"Creating {role} message in session: {session_id}")
        
        try:
            new_message = Message(
                session_id=session_id,
                role=role,
                content=content,
                model_name=model_name,
                token_count=token_count
            )
            
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            
            logger.info(f"Message created: {new_message.id} (role: {role})")
            return new_message
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create message in session {session_id}: Session may not exist")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating message in session {session_id}: {str(e)}")
            raise
    
    def get_messages_by_session(self, session_id: uuid.UUID) -> list[Message]:
        """
        Retrieves all messages in a chat session, ordered chronologically.
        
        Args:
            session_id: The session's UUID
            
        Returns:
            list[Message]: List of messages, ordered by created_at ascending
        """
        logger.info(f"Fetching all messages for session: {session_id}")
        
        messages = (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        
        logger.info(f"Found {len(messages)} messages in session {session_id}")
        return messages
    
    def get_messages_by_session_exclude_system(self, session_id: uuid.UUID) -> list[Message]:
        """
        Retrieves all messages in a session, excluding 'system' role messages.
        Useful for displaying conversation history to users.
        
        Args:
            session_id: The session's UUID
            
        Returns:
            list[Message]: List of messages (user and assistant only)
        """
        logger.info(f"Fetching non-system messages for session: {session_id}")
        
        messages = (
            self.db.query(Message)
            .filter(
                Message.session_id == session_id,
                Message.role != "system"
            )
            .order_by(Message.created_at.asc())
            .all()
        )
        
        logger.info(f"Found {len(messages)} non-system messages in session {session_id}")
        return messages
    
    def delete_messages_by_session(self, session_id: uuid.UUID) -> int:
        """
        Deletes all messages in a chat session.
        
        Args:
            session_id: The session's UUID
            
        Returns:
            int: Number of messages deleted
        """
        logger.info(f"Deleting all messages in session: {session_id}")
        
        try:
            deleted_count = (
                self.db.query(Message)
                .filter(Message.session_id == session_id)
                .delete()
            )
            
            self.db.commit()
            logger.info(f"Deleted {deleted_count} messages from session {session_id}")
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete messages from session {session_id}: {str(e)}")
            raise
    
    def get_last_message_by_session(self, session_id: uuid.UUID) -> Message | None:
        """
        Retrieves the most recent message in a session.
        
        Args:
            session_id: The session's UUID
            
        Returns:
            Message | None: The last message if exists, None otherwise
        """
        logger.info(f"Fetching last message for session: {session_id}")
        
        message = (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .first()
        )
        
        if message:
            logger.info(f"Last message found: {message.id} (role: {message.role})")
        else:
            logger.warning(f"No messages found in session: {session_id}")
        
        return message
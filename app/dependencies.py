# app/dependencies.py

from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db
from database.repositories import UserRepository, ChatSessionRepository, MessageRepository
from services.chatbot_service import ChatbotService

# =====================================================================
# Repository Dependencies
# =====================================================================

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Injects the DB session into the UserRepository."""
    return UserRepository(db)

def get_session_repository(db: Session = Depends(get_db)) -> ChatSessionRepository:
    """Injects the DB session into the ChatSessionRepository."""
    return ChatSessionRepository(db)

def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    """Injects the DB session into the MessageRepository."""
    return MessageRepository(db)

# =====================================================================
# Service Dependencies
# =====================================================================

def get_chatbot_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
) -> ChatbotService:
    """
    Dependency provider for ChatbotService.
    FastAPI will instantiate this service PER REQUEST, injecting the 
    repositories which already contain the current request's DB session.
    """
    return ChatbotService(user_repo, session_repo, message_repo)
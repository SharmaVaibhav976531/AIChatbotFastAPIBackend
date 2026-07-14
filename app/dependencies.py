# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.session import get_db
from database.repositories import UserRepository, ChatSessionRepository, MessageRepository
from database.models.user import User
from services.chatbot_service import ChatbotService
from services.auth_service import AuthService
from services.user_service import UserService
from services.session_service import SessionService
from services.jwt_service import JWTService
import uuid
import logging

logger = logging.getLogger(__name__)

# OAuth2PasswordBearer tells FastAPI:
#   1. Where to find the token: Authorization: Bearer <token>
#   2. Where the login endpoint is: /auth/login (for Swagger UI's "Authorize" button)
#   3. auto_error=False on optional variant: Don't raise 401 automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# =====================================================================
# Repository Dependencies (UNCHANGED from Phase 2)
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

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService(user_repo)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Dependency provider for UserService."""
    return UserService(user_repo)

def get_session_service(
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
) -> SessionService:
    """Dependency provider for SessionService."""
    return SessionService(session_repo, message_repo)


# =====================================================================
# Authentication Dependencies
# =====================================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    CORE AUTH DEPENDENCY — Extracts and validates the JWT from the request.
    
    This is the primary gate for protected routes. If the token is:
      - Missing → 401 (handled by OAuth2PasswordBearer)
      - Invalid/Expired → 401 (raised here)
      - Valid → Returns the User object
    
    Usage in routes:
        @router.get("/protected")
        async def protected(user: User = Depends(get_current_user)):
            return {"hello": user.username}
    """
    # 1. Verify the token
    payload = JWTService.verify_access_token(token)
    if not payload:
        logger.warning("[AUTH-DEP] Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Extract user ID from token claims
    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("[AUTH-DEP] Token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Look up the user in the database
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.get_user_by_id(user_id)
    if not user:
        logger.warning(f"[AUTH-DEP] User from token not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    user: User = Depends(get_current_user)
) -> User:
    """
    Extends get_current_user with an active check.
    Use this for routes that require the user to be active.
    
    An admin could deactivate a user's account (e.g., for abuse).
    Their token would still be valid, but this check blocks them.
    """
    if not user.is_active:
        logger.warning(f"[AUTH-DEP] Inactive user tried to access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    return user


def get_optional_user(
    token: str | None = Depends(oauth2_scheme_optional),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User | None:
    """
    Optional auth dependency — returns None if no token is provided.
    
    Use this for routes that work for both authenticated and anonymous users.
    Example: The /health endpoint might show extra info for logged-in users.
    """
    if not token:
        return None
    
    payload = JWTService.verify_access_token(token)
    if not payload:
        return None
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    try:
        return user_repo.get_user_by_id(uuid.UUID(user_id_str))
    except (ValueError, Exception):
        return None


def get_admin_user(
    user: User = Depends(get_current_active_user)
) -> User:
    """
    Admin-only dependency — future-ready for admin endpoints.
    Requires the user to be both active AND a superuser.
    """
    if not user.is_superuser:
        logger.warning(f"[AUTH-DEP] Non-admin user tried to access admin route: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
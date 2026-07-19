# app/dependencies.py

from core.settings import get_settings
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
from services.cache_service import CacheService
from redis_client.client import get_redis_client
from fastapi import Request, Depends, HTTPException, status
from services.storage_service import StorageService
from storage.local import LocalStorageProvider
from services.loader_service import LoaderService
from services.chunking_service import ChunkingService
from services.metadata_service import MetadataService
from services.embedding_service import EmbeddingService, embedding_provider
from services.retrieval_service import RetrievalService
from services.vector_search_service import VectorSearchService
from services.reranking_service import RerankingService
from services.context_builder_service import ContextBuilderService
from services.grounding_service import GroundingService
from services.prompt_builder_service import PromptBuilderService
from services.rag_service import RAGService
from database.repositories.embedding_repository import EmbeddingRepository
from database.repositories.vector_repository import VectorRepository
from database.repositories.search_repository import SearchRepository
from utils.educational_logger import EducationalLogger
import uuid
import logging

logger = logging.getLogger(__name__)

# Log file execution details for architecture learning
EducationalLogger.log_file_execution(
    file_name="app/dependencies.py",
    purpose="Centralized Dependency Injection Provider for FastAPI routes.",
    responsibilities=[
        "Inject database sessions into repositories",
        "Inject repositories into service layer instances",
        "Validate OAuth2 Bearer JWT tokens and authenticate users",
        "Instantiate singleton and per-request services for routes"
    ]
)

loader_service = LoaderService() # Initialize the loader service (Singleton)
settings = get_settings()  # Initialize the settings (Singleton)
chunking_service = ChunkingService() # Initialize the chunking service (Singleton)

# Initialize the services (Singletons)
metadata_service = MetadataService()
embedding_service = EmbeddingService(provider=embedding_provider)

# Phase 7 Stateless Services (Singletons)
reranking_service = RerankingService()
context_builder_service = ContextBuilderService()
grounding_service = GroundingService()
prompt_builder_service = PromptBuilderService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Initialize the storage provider (Singleton pattern for the app lifecycle)
storage_provider = LocalStorageProvider(base_dir=settings.upload_directory)
storage_service = StorageService(provider=storage_provider)


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

def get_embedding_repository(db: Session = Depends(get_db)) -> EmbeddingRepository:
    """Injects the DB session into the EmbeddingRepository."""
    return EmbeddingRepository(db)

def get_vector_repository(db: Session = Depends(get_db)) -> VectorRepository:
    """Injects the DB session into the VectorRepository."""
    return VectorRepository(db)

def get_search_repository(db: Session = Depends(get_db)) -> SearchRepository:
    """Injects the DB session into the SearchRepository."""
    return SearchRepository(db)

def get_retrieval_service(
    embedding_repo: EmbeddingRepository = Depends(get_embedding_repository),
) -> RetrievalService:
    """Dependency provider for RetrievalService."""
    return RetrievalService(embedding_repo, embedding_service)

def get_cache_service(redis_client = Depends(get_redis_client)) -> CacheService:
    """
    Dependency provider for CacheService.
    Injects the Redis client (which may be None if Redis is down).
    """
    return CacheService(redis_client)

def get_vector_search_service(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    cache_svc: CacheService = Depends(get_cache_service)
) -> VectorSearchService:
    """Dependency provider for Phase 6 VectorSearchService."""
    return VectorSearchService(
        vector_repo=vector_repo,
        embedding_service=embedding_service,
        cache_service=cache_svc
    )

def get_reranking_service() -> RerankingService:
    return reranking_service

def get_context_builder_service() -> ContextBuilderService:
    return context_builder_service

def get_grounding_service() -> GroundingService:
    return grounding_service

def get_prompt_builder_service() -> PromptBuilderService:
    return prompt_builder_service

def get_rag_service(
    vector_search_svc: VectorSearchService = Depends(get_vector_search_service),
    cache_svc: CacheService = Depends(get_cache_service)
) -> RAGService:
    """Dependency provider for Phase 7 RAGService."""
    return RAGService(
        vector_search_service=vector_search_svc,
        reranking_service=reranking_service,
        context_builder_service=context_builder_service,
        grounding_service=grounding_service,
        prompt_builder_service=prompt_builder_service,
        cache_service=cache_svc
    )

def get_chatbot_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository),
    retrieval_svc: RetrievalService = Depends(get_retrieval_service),
    rag_svc: RAGService = Depends(get_rag_service)
) -> ChatbotService:
    """
    Dependency provider for ChatbotService.
    FastAPI will instantiate this service PER REQUEST, injecting the 
    repositories which already contain the current request's DB session.
    """
    return ChatbotService(user_repo, session_repo, message_repo, retrieval_svc, rag_svc)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService(user_repo)

def get_cache_service(redis_client = Depends(get_redis_client)) -> CacheService:
    """
    Dependency provider for CacheService.
    Injects the Redis client (which may be None if Redis is down).
    """
    return CacheService(redis_client)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    cache_service: CacheService = Depends(get_cache_service)
) -> UserService:
    return UserService(user_repo, cache_service)

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
    start_time = EducationalLogger.log_function_enter(
        file_name="app/dependencies.py",
        class_name=None,
        func_name="get_current_user",
        purpose="Authenticate request using Bearer JWT token and fetch user from DB.",
        input_params={"token": f"{token[:15]}..." if token else None}
    )
    
    # 1. Verify the token
    payload = JWTService.verify_access_token(token)
    if not payload:
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Invalid Token", start_time, "FAILED")
        logger.warning("[AUTH-DEP] Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Extract user ID from token claims
    user_id_str = payload.get("sub")
    if not user_id_str:
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Missing sub claim", start_time, "FAILED")
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
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", f"User {user_id} not found", start_time, "FAILED")
        logger.warning(f"[AUTH-DEP] User from token not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", f"User(username='{user.username}')", start_time, "SUCCESS")
    return user


def get_current_active_user(
    request: Request,  # 1. Inject the Request object
    user: User = Depends(get_current_user)
) -> User:
    # 2. Attach the validated user to request.state 
    # This allows SlowAPI's key_func to safely access req.state.user.id
    request.state.user = user
    
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


def get_storage_service() -> StorageService:
    """Dependency provider for StorageService."""
    return storage_service

def get_loader_service() -> LoaderService:
    """Dependency provider for LoaderService."""
    return loader_service

def get_chunking_service() -> ChunkingService:
    """Dependency provider for ChunkingService."""
    return chunking_service

def get_metadata_service() -> MetadataService:
    """Dependency provider for MetadataService."""
    return metadata_service

def get_embedding_service() -> EmbeddingService:
    """Dependency provider for EmbeddingService."""
    return embedding_service


# =====================================================================
# Document Dependencies (Phase 5)
# =====================================================================
from database.repositories.document_repository import DocumentRepository
from services.document_service import DocumentService

def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    """Injects the DB session into the DocumentRepository."""
    return DocumentRepository(db)

def get_document_service(
    doc_repo: DocumentRepository = Depends(get_document_repository),
    storage_svc: StorageService = Depends(get_storage_service)
) -> DocumentService:
    """Dependency provider for DocumentService."""
    return DocumentService(doc_repo, storage_svc)
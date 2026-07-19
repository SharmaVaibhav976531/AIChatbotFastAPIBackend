# app/dependencies.py

"""
FastAPI Dependency Injection Module.
Centralized location for providing instances of Repositories, Services, Agents, and Database Sessions.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid
import logging

from database.session import get_db
from database.repositories import (
    UserRepository, ChatSessionRepository, MessageRepository, DocumentRepository, EmbeddingRepository, VectorRepository
)
from database.repositories.search_repository import SearchRepository
from services.user_service import UserService
from services.auth_service import AuthService
from services.jwt_service import JWTService
from services.session_service import SessionService
from services.chatbot_service import ChatbotService
from services.loader_service import LoaderService
from services.chunking_service import ChunkingService
from services.embedding_service import EmbeddingService, embedding_provider
from services.retrieval_service import RetrievalService
from services.vector_search_service import VectorSearchService
from services.reranking_service import RerankingService
from services.context_builder_service import ContextBuilderService
from services.grounding_service import GroundingService
from services.prompt_builder_service import PromptBuilderService
from services.cache_service import CacheService
from services.rag_service import RAGService
from services.memory_service import MemoryService
from services.query_expansion_service import QueryExpansionService
from services.hyde_service import HyDEService
from services.multi_query_service import MultiQueryService
from services.parent_child_service import ParentChildService
from services.context_compression_service import ContextCompressionService
from services.document_service import DocumentService
from services.storage_service import StorageService
from storage.local import LocalStorageProvider
from core.settings import get_settings

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.tool_router import ToolRouter
from agents.tools.calculator_tool import CalculatorTool
from agents.tools.python_repl_tool import PythonREPLTool
from agents.tools.search_tool import SearchTool
from agents.tools.rag_bridge_tool import RAGBridgeTool

from database.models.user import User
from redis_client import get_redis_client
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

# Single OAuth2 scheme instance across the app
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

EducationalLogger.log_file_execution(
    file_name="app/dependencies.py",
    purpose="FastAPI Dependency Injection container wiring Repositories, Services, Agents and Security handlers.",
    responsibilities=[
        "Supply request-scoped SQLAlchemy Session",
        "Instantiate UserRepository, ChatSessionRepository, MessageRepository, DocumentRepository, SearchRepository, VectorRepository",
        "Wire CacheService, RAGService, MemoryService, DocumentService, PlannerAgent, ExecutorAgent, ToolRouter",
        "Enforce Bearer JWT OAuth2 Security"
    ]
)


# Repositories
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_session_repository(db: Session = Depends(get_db)) -> ChatSessionRepository:
    return ChatSessionRepository(db)

def get_message_repository(db: Session = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)

def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)

def get_embedding_repository(db: Session = Depends(get_db)) -> EmbeddingRepository:
    return EmbeddingRepository(db)

def get_vector_repository(db: Session = Depends(get_db)) -> VectorRepository:
    return VectorRepository(db)

def get_search_repository(db: Session = Depends(get_db)) -> SearchRepository:
    return SearchRepository(db)


# Storage & Document Service Providers
def get_storage_service() -> StorageService:
    provider = LocalStorageProvider(base_dir=get_settings().upload_directory)
    return StorageService(provider)

def get_document_service(
    doc_repo: DocumentRepository = Depends(get_document_repository),
    storage_svc: StorageService = Depends(get_storage_service)
) -> DocumentService:
    return DocumentService(doc_repo, storage_svc)


# Cache & Memory Services
def get_cache_service(redis_client = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client)

def get_memory_service(cache_svc: CacheService = Depends(get_cache_service)) -> MemoryService:
    return MemoryService(cache_svc)


# RAG Pipeline Component Services
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(provider=embedding_provider)

def get_retrieval_service(
    embedding_repo: EmbeddingRepository = Depends(get_embedding_repository),
    embedding_svc: EmbeddingService = Depends(get_embedding_service)
) -> RetrievalService:
    return RetrievalService(embedding_repo, embedding_svc)

def get_vector_search_service(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    embedding_svc: EmbeddingService = Depends(get_embedding_service),
    cache_svc: CacheService = Depends(get_cache_service)
) -> VectorSearchService:
    return VectorSearchService(
        vector_repo=vector_repo,
        embedding_service=embedding_svc,
        cache_service=cache_svc
    )

def get_reranking_service() -> RerankingService:
    return RerankingService()

def get_context_builder_service() -> ContextBuilderService:
    return ContextBuilderService()

def get_grounding_service() -> GroundingService:
    return GroundingService()

def get_prompt_builder_service() -> PromptBuilderService:
    return PromptBuilderService()

def get_query_expansion_service() -> QueryExpansionService:
    return QueryExpansionService()

def get_hyde_service() -> HyDEService:
    return HyDEService()

def get_multi_query_service(
    embedding_repo: EmbeddingRepository = Depends(get_embedding_repository),
    embedding_svc: EmbeddingService = Depends(get_embedding_service)
) -> MultiQueryService:
    return MultiQueryService(embedding_repo, embedding_svc)

def get_parent_child_service(db: Session = Depends(get_db)) -> ParentChildService:
    return ParentChildService(db)

def get_context_compression_service() -> ContextCompressionService:
    return ContextCompressionService()


def get_rag_service(
    vector_search_svc: VectorSearchService = Depends(get_vector_search_service),
    reranking_svc: RerankingService = Depends(get_reranking_service),
    context_builder_svc: ContextBuilderService = Depends(get_context_builder_service),
    grounding_svc: GroundingService = Depends(get_grounding_service),
    prompt_builder_svc: PromptBuilderService = Depends(get_prompt_builder_service),
    cache_svc: CacheService = Depends(get_cache_service),
    query_expansion_svc: QueryExpansionService = Depends(get_query_expansion_service),
    hyde_svc: HyDEService = Depends(get_hyde_service),
    multi_query_svc: MultiQueryService = Depends(get_multi_query_service),
    parent_child_svc: ParentChildService = Depends(get_parent_child_service),
    context_compression_svc: ContextCompressionService = Depends(get_context_compression_service)
) -> RAGService:
    return RAGService(
        vector_search_service=vector_search_svc,
        reranking_service=reranking_svc,
        context_builder_service=context_builder_svc,
        grounding_service=grounding_svc,
        prompt_builder_service=prompt_builder_svc,
        cache_service=cache_svc,
        query_expansion_service=query_expansion_svc,
        hyde_service=hyde_svc,
        multi_query_service=multi_query_svc,
        parent_child_service=parent_child_svc,
        context_compression_service=context_compression_svc
    )


# Agent & Tool Dependencies
def get_calculator_tool() -> CalculatorTool:
    return CalculatorTool()

def get_python_repl_tool() -> PythonREPLTool:
    return PythonREPLTool()

def get_search_tool() -> SearchTool:
    return SearchTool()

def get_rag_bridge_tool(retrieval_svc: RetrievalService = Depends(get_retrieval_service)) -> RAGBridgeTool:
    return RAGBridgeTool(retrieval_svc)

def get_tool_router(
    calc_tool: CalculatorTool = Depends(get_calculator_tool),
    py_tool: PythonREPLTool = Depends(get_python_repl_tool),
    srch_tool: SearchTool = Depends(get_search_tool),
    rag_bridge: RAGBridgeTool = Depends(get_rag_bridge_tool)
) -> ToolRouter:
    return ToolRouter(calc_tool, py_tool, srch_tool, rag_bridge)

def get_planner_agent() -> PlannerAgent:
    return PlannerAgent()

def get_executor_agent(tool_router: ToolRouter = Depends(get_tool_router)) -> ExecutorAgent:
    return ExecutorAgent(tool_router)


def get_chatbot_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository),
    retrieval_svc: RetrievalService = Depends(get_retrieval_service),
    rag_svc: RAGService = Depends(get_rag_service),
    memory_svc: MemoryService = Depends(get_memory_service),
    planner_agent: PlannerAgent = Depends(get_planner_agent),
    executor_agent: ExecutorAgent = Depends(get_executor_agent)
) -> ChatbotService:
    return ChatbotService(
        user_repo=user_repo,
        session_repo=session_repo,
        message_repo=message_repo,
        retrieval_service=retrieval_svc,
        rag_service=rag_svc,
        memory_service=memory_svc,
        planner_agent=planner_agent,
        executor_agent=executor_agent
    )

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    cache_service: CacheService = Depends(get_cache_service)
) -> UserService:
    return UserService(user_repo, cache_service)

def get_session_service(
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
) -> SessionService:
    return SessionService(session_repo, message_repo)


# Security & Current User Auth
def get_current_user(
    request: Request,
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
    
    payload = JWTService.verify_access_token(token)
    if not payload:
        EducationalLogger.log_auth_event("JWT Verification", "Unknown", False, "Invalid or expired access token")
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Invalid Token", start_time, "FAILED")
        logger.warning("[AUTH-DEP] Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        EducationalLogger.log_auth_event("JWT Verification", "Unknown", False, "Token missing sub claim")
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Missing sub", start_time, "FAILED")
        logger.warning("[AUTH-DEP] JWT payload missing sub claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        EducationalLogger.log_auth_event("JWT Verification", user_id_str, False, "Malformed UUID in token sub")
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Invalid UUID", start_time, "FAILED")
        logger.warning(f"[AUTH-DEP] Invalid UUID in token sub: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.get_user_by_id(user_id)
    if not user:
        EducationalLogger.log_auth_event("DB User Lookup", user_id_str, False, "User ID not found in database")
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "User Not Found", start_time, "FAILED")
        logger.warning(f"[AUTH-DEP] User {user_id} from token not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        EducationalLogger.log_auth_event("User Status Check", user.username, False, "Account is inactive")
        EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", "Inactive User", start_time, "FAILED")
        logger.warning(f"[AUTH-DEP] Inactive user attempting access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    request.state.user = user
    EducationalLogger.log_auth_event("User Authentication", user.username, True, f"User ID: {user.id}")
    EducationalLogger.log_function_exit("app/dependencies.py", None, "get_current_user", f"User('{user.username}')", start_time, "SUCCESS")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
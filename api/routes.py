# api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from openai import APITimeoutError, APIConnectionError, APIError, AuthenticationError
from schemas.request import ChatRequest
from schemas.response import ChatResponse, HealthResponse, HistoryResponse
from services.chatbot_service import ChatbotService
from database.models.user import User
from app.dependencies import get_chatbot_service, get_current_active_user
from core.limiter import limiter
from fastapi import Request
import logging
import time
from uuid import UUID
from services.health_service import health_service
from monitoring.metrics import get_metrics, get_metrics_content_type
from core.settings import get_settings

from utils.educational_logger import EducationalLogger

settings = get_settings()

logger = logging.getLogger(__name__)
router = APIRouter()

# Log file execution details for architecture learning
EducationalLogger.log_file_execution(
    file_name="api/routes.py",
    purpose="Primary Chat API Router exposing /chat, /history, /reset, and /health endpoints.",
    responsibilities=[
        "Receive HTTP requests from client frontend",
        "Enforce rate-limiting middleware (SlowAPI)",
        "Trigger user authentication dependencies",
        "Delegate chat message processing to ChatbotService",
        "Log request execution tree upon completion"
    ]
)


# ══════════════════════════════════════════════════════════════════
# GET /health — System health check (PUBLIC — no auth required)
# ══════════════════════════════════════════════════════════════════
@router.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    EducationalLogger.log_function_intent(
        target_func="health_service.get_overall_health",
        reason="Check status of DB, Redis, Celery, and OpenRouter prior to responding.",
        input_desc="None",
        expected_output="Health status dict"
    )
    health_data = health_service.get_overall_health()
    
    # If database is down, return 503 Service Unavailable
    if health_data["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )
    
    return health_data


# ══════════════════════════════════════════════════════════════════
# POST /chat — Send message, get AI reply (PROTECTED)
# ══════════════════════════════════════════════════════════════════
@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
@limiter.limit("20/minute", key_func=lambda request: f"user:{request.state.user.id}")
async def chat(
    request: Request, # Required by SlowAPI
    chat_data: ChatRequest,
    user: User = Depends(get_current_active_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    start_time = EducationalLogger.log_function_enter(
        file_name="api/routes.py",
        class_name=None,
        func_name="chat",
        purpose="HTTP Route Handler for processing user chat message and generating AI reply.",
        input_params={"user": user.username, "session_id": chat_data.session_id, "message_preview": f"'{chat_data.message[:30]}...'"}
    )
    
    EducationalLogger.log_function_intent(
        target_func="ChatbotService.get_response",
        reason="Execute core business logic: session resolution, RAG context retrieval, LLM call, and DB message persistence.",
        input_desc=f"message='{chat_data.message[:30]}...', user={user.username}, session_id={chat_data.session_id}",
        expected_output="AI response string"
    )
    
    try:
        reply = service.get_response(
            user_message=chat_data.message,
            user=user,
            session_id=chat_data.session_id
        )
        
        EducationalLogger.log_function_exit("api/routes.py", None, "chat", f"ChatResponse(reply='{reply[:40]}...')", start_time, "SUCCESS")
        
        # Educational Execution Tree Summary
        EducationalLogger.log_execution_tree([
            "Frontend (Browser HTTP POST /chat)",
            "APIRouter (api/routes.py:chat)",
            "OAuth2 Dependency (app/dependencies.py:get_current_active_user)",
            "ChatbotService (services/chatbot_service.py:get_response)",
            "RetrievalService / RAGService (services/retrieval_service.py:retrieve_context)",
            "EmbeddingRepository (database/repositories/embedding_repository.py:search_similar)",
            "PostgreSQL Database (embeddings + document_chunks + documents tables)",
            "OpenRouter LLM API (Inference with injected RAG context)",
            "MessageRepository (database/repositories/message_repository.py:create_message)",
            "Frontend (HTTP 200 OK JSON ChatResponse)"
        ])
        
        return ChatResponse(reply=reply, model=service.settings.model_name)
    except AuthenticationError as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 61, e, chat_data.message, "AI Reply", "Verify OPENROUTER_API_KEY in .env")
        raise HTTPException(status_code=500, detail="Invalid AI service API key configuration.")
    except APITimeoutError as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 63, e, chat_data.message, "AI Reply", "OpenRouter timed out. Retry request.")
        raise HTTPException(status_code=504, detail="The AI service took too long to respond.")
    except APIConnectionError as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 65, e, chat_data.message, "AI Reply", "Check network connection to OpenRouter.")
        raise HTTPException(status_code=503, detail="Could not connect to the AI service.")
    except APIError as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 67, e, chat_data.message, "AI Reply", "Review OpenRouter error message details.")
        raise HTTPException(status_code=502, detail=f"AI service returned an error: {str(e)}")
    except ValueError as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 69, e, chat_data.message, "AI Reply", "Check input parameters.")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        EducationalLogger.log_educational_error("api/routes.py", "chat", 71, e, chat_data.message, "AI Reply", "Inspect trace log for unhandled exception.")
        logger.error(f"[CHAT ROUTE ERROR] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


# ══════════════════════════════════════════════════════════════════
# POST /reset — Clear conversation history (PROTECTED)
# ══════════════════════════════════════════════════════════════════
@router.post("/reset", status_code=status.HTTP_200_OK, tags=["Chat"])
async def reset_conversation(
    user: User = Depends(get_current_active_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Reset the current session's conversation history.
    
    PHASE 3 CHANGES:
    - Now requires authentication  
    - Resets only the authenticated user's latest session
    """
    service.reset_conversation(user=user)
    return {"message": "Conversation history has been cleared."}


# ══════════════════════════════════════════════════════════════════
# GET /history — Retrieve conversation history (PROTECTED)
# ══════════════════════════════════════════════════════════════════
@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
async def get_history(
    user: User = Depends(get_current_active_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Retrieve the conversation history for the current session.
    
    PHASE 3 CHANGES:
    - Now requires authentication
    - Returns only the authenticated user's history
    """
    history = service.get_history(user=user)
    return HistoryResponse(history=history)


# ══════════════════════════════════════════════════════════════════
# GET /metrics — Prometheus Metrics Endpoint (PUBLIC/PROTECTED)
# ══════════════════════════════════════════════════════════════════
@router.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Exposes Prometheus metrics.
    In production, this should be protected by network rules (e.g., only accessible 
    from the Prometheus server IP or via a specific internal port).
    """
    from fastapi.responses import Response
    return Response(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )
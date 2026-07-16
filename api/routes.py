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

settings = get_settings()

logger = logging.getLogger(__name__)
router = APIRouter()



# ══════════════════════════════════════════════════════════════════
# GET /health — System health check (PUBLIC — no auth required)
# ══════════════════════════════════════════════════════════════════
@router.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():

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
    try:
        reply = service.get_response(
            user_message=chat_data.message,
            user=user,
            session_id=chat_data.session_id
        )
        return ChatResponse(reply=reply, model=service.settings.model_name)
    except AuthenticationError:
        raise HTTPException(status_code=500, detail="Invalid AI service API key configuration.")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="The AI service took too long to respond.")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to the AI service.")
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service returned an error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
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
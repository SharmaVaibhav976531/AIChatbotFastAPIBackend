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

logger = logging.getLogger(__name__)
router = APIRouter()



# ══════════════════════════════════════════════════════════════════
# GET /health — System health check (PUBLIC — no auth required)
# ══════════════════════════════════════════════════════════════════
@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    response = HealthResponse(status="healthy")
    return response


# ══════════════════════════════════════════════════════════════════
# POST /chat — Send message, get AI reply (PROTECTED)
# ══════════════════════════════════════════════════════════════════
@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
@limiter.limit("20/minute", key_func=lambda req: f"user:{req.state.user.id}")
async def chat(
    request: Request, # Required by SlowAPI
    chat_data: ChatRequest,
    user: User = Depends(get_current_active_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    try:
        reply = service.get_response(
            user_message=request.message,
            user=user,
            session_id=getattr(request, 'session_id', None)
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
    except Exception as e:
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
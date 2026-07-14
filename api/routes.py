# api/routes.py
# ══════════════════════════════════════════════════════════════════
# CORE CHAT ROUTES — Health, Chat, Reset, History
# ══════════════════════════════════════════════════════════════════
#
# WHY THIS FILE EXISTS:
#   These are the ORIGINAL Phase 1/2 routes, now upgraded with authentication.
#   The /chat, /history, and /reset endpoints now require authentication
#   and operate on the user's own sessions.
#
# WHAT CHANGED IN PHASE 3:
#   - Added get_current_active_user dependency to protected routes
#   - Chat now accepts optional session_id to target a specific session
#   - History loads from the user's current session (not a shared "guest")
#   - Reset clears the user's current session (not a shared "guest")
#   - /health remains PUBLIC (no auth required)
#
# HOW IT CONNECTS:
#   - Registered in app/main.py (unchanged)
#   - ChatbotService now accepts user and session_id parameters
#

from fastapi import APIRouter, Depends, HTTPException, status
from openai import APITimeoutError, APIConnectionError, APIError, AuthenticationError
from schemas.request import ChatRequest
from schemas.response import ChatResponse, HealthResponse, HistoryResponse
from services.chatbot_service import ChatbotService
from database.models.user import User
from app.dependencies import get_chatbot_service, get_current_active_user
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
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_active_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Send a message and receive an AI response.
    
    PHASE 3 CHANGES:
    - Now requires authentication
    - Uses the authenticated user (not "guest")
    - Accepts optional session_id in the request body
    - If no session_id, uses the user's latest session (or creates one)
    """
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
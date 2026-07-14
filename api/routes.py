# api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from openai import APITimeoutError, APIConnectionError, APIError, AuthenticationError
from schemas.request import ChatRequest
from schemas.response import ChatResponse, HealthResponse, HistoryResponse
from services.chatbot_service import ChatbotService
from app.dependencies import get_chatbot_service
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()



# ══════════════════════════════════════════════════════════════════
# GET /health — System health check
# ══════════════════════════════════════════════════════════════════
@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    response = HealthResponse(status="healthy")
    return response


# ══════════════════════════════════════════════════════════════════
# POST /chat — Send message, get AI reply
# ══════════════════════════════════════════════════════════════════
@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
async def chat(request: ChatRequest, service: ChatbotService = Depends(get_chatbot_service)):
    try:
        reply = service.get_response(request.message)
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
# POST /reset — Clear conversation history
# ══════════════════════════════════════════════════════════════════
@router.post("/reset", status_code=status.HTTP_200_OK, tags=["Chat"])
async def reset_conversation(service: ChatbotService = Depends(get_chatbot_service)):
    service.reset_conversation()
    return {"message": "Conversation history has been cleared."}


# ══════════════════════════════════════════════════════════════════
# GET /history — Retrieve conversation history
# ══════════════════════════════════════════════════════════════════
@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
async def get_history(service: ChatbotService = Depends(get_chatbot_service)):
    history = service.get_history()
    return HistoryResponse(history=history)
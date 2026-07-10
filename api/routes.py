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

logger.info("[ROUTES] Defining API endpoint handlers...")


# ══════════════════════════════════════════════════════════════════
# GET /health — System health check
# ══════════════════════════════════════════════════════════════════
@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    logger.info("[ROUTE] health_check() CALLED")
    response = HealthResponse(status="healthy")
    logger.info(f"[ROUTE] health_check() → returning status='{response.status}'")
    return response


# ══════════════════════════════════════════════════════════════════
# POST /chat — Send message, get AI reply
# ══════════════════════════════════════════════════════════════════
@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
async def chat(request: ChatRequest, service: ChatbotService = Depends(get_chatbot_service)):
    route_start = time.time()
    preview = request.message[:100] + "..." if len(request.message) > 100 else request.message
    logger.info(f"[ROUTE] chat() CALLED")
    logger.info(f"[ROUTE]   → Validated message: ({len(request.message)} chars) \"{preview}\"")
    logger.info(f"[ROUTE]   → Calling service.get_response()...")

    try:
        reply = service.get_response(request.message)

        reply_preview = reply[:150] + "..." if len(reply) > 150 else reply
        route_ms = (time.time() - route_start) * 1000
        logger.info(f"[ROUTE] chat() → AI reply: ({len(reply)} chars) \"{reply_preview}\"")
        logger.info(f"[ROUTE] chat() → model: {service.settings.model_name}")
        logger.info(f"[ROUTE] chat() COMPLETED in {route_ms:.1f}ms")

        return ChatResponse(reply=reply, model=service.settings.model_name)

    except AuthenticationError:
        logger.error("[ROUTE] chat() ❌ AuthenticationError → HTTP 500")
        raise HTTPException(status_code=500, detail="Invalid AI service API key configuration.")
    except APITimeoutError:
        logger.error("[ROUTE] chat() ❌ APITimeoutError → HTTP 504")
        raise HTTPException(status_code=504, detail="The AI service took too long to respond.")
    except APIConnectionError:
        logger.error("[ROUTE] chat() ❌ APIConnectionError → HTTP 503")
        raise HTTPException(status_code=503, detail="Could not connect to the AI service.")
    except APIError as e:
        logger.error(f"[ROUTE] chat() ❌ APIError → HTTP 502: {e}")
        raise HTTPException(status_code=502, detail=f"AI service returned an error: {str(e)}")
    except Exception as e:
        logger.exception(f"[ROUTE] chat() ❌ Unexpected {type(e).__name__} → HTTP 500")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


# ══════════════════════════════════════════════════════════════════
# POST /reset — Clear conversation history
# ══════════════════════════════════════════════════════════════════
@router.post("/reset", status_code=status.HTTP_200_OK, tags=["Chat"])
async def reset_conversation(service: ChatbotService = Depends(get_chatbot_service)):
    logger.info("[ROUTE] reset_conversation() CALLED")
    history_size = len(service.get_history())
    logger.info(f"[ROUTE]   → Current history: {history_size} messages")
    service.reset_conversation()
    logger.info("[ROUTE] reset_conversation() COMPLETED → history cleared")
    return {"message": "Conversation history has been cleared."}


# ══════════════════════════════════════════════════════════════════
# GET /history — Retrieve conversation history
# ══════════════════════════════════════════════════════════════════
@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
async def get_history(service: ChatbotService = Depends(get_chatbot_service)):
    logger.info("[ROUTE] get_history() CALLED")
    history = service.get_history()
    logger.info(f"[ROUTE] get_history() → returning {len(history)} messages")
    if not history:
        logger.info("[ROUTE]   → History is empty (no messages yet)")
    return HistoryResponse(history=history)


logger.info("[ROUTES] ✅ All endpoint handlers defined")
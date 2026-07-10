from services.chatbot_service import ChatbotService
import logging

logger = logging.getLogger(__name__)

# Create a single instance (Singleton) so conversation history is shared across requests
logger.info("[DEPENDENCY] Creating singleton ChatbotService instance...")
chatbot_service = ChatbotService()
logger.info("[DEPENDENCY] ✅ Singleton ChatbotService ready for injection")


def get_chatbot_service() -> ChatbotService:
    """Dependency provider for the ChatbotService."""
    logger.debug("[DEPENDENCY] get_chatbot_service() → injecting singleton into route handler")
    return chatbot_service
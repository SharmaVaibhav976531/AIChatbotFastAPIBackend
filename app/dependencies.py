from services.chatbot_service import ChatbotService

# Create a single instance (Singleton) so conversation history is shared across requests
chatbot_service = ChatbotService()

def get_chatbot_service() -> ChatbotService:
    """Dependency provider for the ChatbotService."""
    return chatbot_service
from services.chatbot_service import ChatbotService

chatbot_service = ChatbotService()

def get_chatbot_service() -> ChatbotService:
    return chatbot_service
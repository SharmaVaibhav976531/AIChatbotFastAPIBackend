from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, AuthenticationError
from core.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.openrouter_api_key,
            timeout=30.0,
            max_retries=3,
        )
        self.system_prompt = "You are a helpful, concise AI assistant."
        # In-memory conversation history
        self.messages: list[dict] = [{"role": "system", "content": self.system_prompt}]
        
    def get_response(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        
        try:
            logger.info(f"Sending request to OpenRouter. Message count: {len(self.messages)}")
            completion = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=self.messages,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                top_p=self.settings.top_p,
                frequency_penalty=self.settings.frequency_penalty,
            )
            
            if completion and completion.choices:
                reply = completion.choices[0].message.content
                self.messages.append({"role": "assistant", "content": reply})
                logger.info("Successfully received response from OpenRouter.")
                return reply
            return "[No choices returned by the API]"
            
        except AuthenticationError:
            logger.error("Authentication failed: Invalid API key.")
            raise
        except APITimeoutError:
            logger.error("OpenRouter API request timed out.")
            raise
        except APIConnectionError:
            logger.error("Failed to connect to OpenRouter.")
            raise
        except APIError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chatbot service: {e}")
            raise
            
    def reset_conversation(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
        logger.info("Conversation history has been reset.")
        
    def get_history(self) -> list[dict]:
        # Exclude system prompt for a cleaner history view
        return [msg for msg in self.messages if msg["role"] != "system"]
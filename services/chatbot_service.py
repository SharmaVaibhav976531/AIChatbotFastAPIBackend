# services/chatbot_service.py

import uuid
import logging
import time
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, AuthenticationError
from core.settings import get_settings
from database.repositories import UserRepository, ChatSessionRepository, MessageRepository
from database.models.user import User
from database.models.session import ChatSession

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Core service that communicates with the AI model via OpenRouter.
    This service is now STATELESS. It relies entirely on the database for conversation history.
    """

    def __init__(
        self, 
        user_repo: UserRepository, 
        session_repo: ChatSessionRepository, 
        message_repo: MessageRepository
    ):
        self.settings = get_settings()
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.openrouter_api_key,
            timeout=30.0,
            max_retries=3,
        )
        self.system_prompt = "You are a helpful, concise AI assistant."
        
        # Repositories injected via FastAPI Dependency Injection
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.message_repo = message_repo

    # =====================================================================
    # HELPER METHODS (Future-proofing for Phase 3 Authentication)
    # =====================================================================
    def _get_default_user(self) -> User:
        """
        Retrieves or creates the default 'guest' user for unauthenticated requests.
        FUTURE-PROOFING: In Phase 3, this will be replaced by the authenticated user from the JWT.
        """
        user = self.user_repo.get_user_by_username("guest")
        if not user:
            logger.info("[SERVICE] Default 'guest' user not found. Creating...")
            user = self.user_repo.create_user(username="guest", email="guest@chatbot.local")
        return user

    def _get_or_create_default_session(self, user_id: uuid.UUID) -> ChatSession:
        """
        Retrieves the active session for the user, or creates a new one.
        FUTURE-PROOFING: In a multi-user app, the frontend will pass a session_id, 
        and this method will fetch that specific session.
        """
        sessions = self.session_repo.get_sessions_by_user(user_id)
        if not sessions:
            logger.info(f"[SERVICE] No active session for user {user_id}. Creating new session...")
            return self.session_repo.create_session(user_id=user_id, title="Default Chat")
        return sessions[0]

    # =====================================================================
    # CORE BUSINESS LOGIC
    # =====================================================================
    def get_response(self, user_message: str) -> str:
        """
        Processes a user message, persists it to DB, loads history, calls the LLM, 
        and persists the AI response.
        """
        func_start = time.time()

        # 1. Resolve User and Session
        user = self._get_default_user()
        session = self._get_or_create_default_session(user.id)
        logger.info(f"[SERVICE] Processing message for session: {session.id}")

        # 2. Save User Message to DB (Done BEFORE calling LLM to prevent data loss on timeout)
        self.message_repo.create_message(
            session_id=session.id,
            role="user",
            content=user_message,
            model_name="N/A"
        )

        # 3. Load Conversation History from DB
        db_messages = self.message_repo.get_messages_by_session(session.id)
        
        # 4. Format Messages for OpenRouter
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})

        try:
            logger.info(f"[SERVICE] Preparing OpenRouter API call:")
            logger.info(f"  → Model             : {self.settings.model_name}")
            logger.info(f"  → Context messages  : {len(messages)}")
            logger.info(f"  → Temperature       : {self.settings.temperature}")
            logger.info(f"  → Max tokens        : {self.settings.max_tokens}")
            logger.info(f"  → Top P             : {self.settings.top_p}")
            logger.info(f"  → Frequency penalty : {self.settings.frequency_penalty}")

            api_start = time.time()

            completion = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                top_p=self.settings.top_p,
                frequency_penalty=self.settings.frequency_penalty,
            )

            api_ms = (time.time() - api_start) * 1000
            logger.info(f"[SERVICE] ✅ OpenRouter responded in {api_ms:.1f}ms")

            if completion and completion.choices:
                reply = completion.choices[0].message.content
                finish = completion.choices[0].finish_reason

                logger.info(f"[SERVICE] Response details:")
                logger.info(f"  → Finish reason : {finish}")
                logger.info(f"  → Reply length  : {len(reply)} chars")

                if completion.usage:
                    logger.info(f"  → Prompt tokens     : {completion.usage.prompt_tokens}")
                    logger.info(f"  → Completion tokens : {completion.usage.completion_tokens}")
                    logger.info(f"  → Total tokens      : {completion.usage.total_tokens}")

                # 5. Save Assistant Message to DB
                self.message_repo.create_message(
                    session_id=session.id,
                    role="assistant",
                    content=reply,
                    model_name=self.settings.model_name,
                    token_count=completion.usage.total_tokens if completion.usage else None
                )
                logger.info(f"[SERVICE] Assistant reply saved to database")

                total_ms = (time.time() - func_start) * 1000
                logger.info(f"[SERVICE] get_response() COMPLETED in {total_ms:.1f}ms")
                logger.info("─" * 50)
                return reply

            logger.warning("[SERVICE] ⚠️ API returned NO CHOICES — empty response")
            return "[No choices returned by the API]"

        except AuthenticationError:
            logger.error("[SERVICE] ❌ AUTH ERROR — API key invalid/expired")
            logger.error("  → Fix: Check OPENROUTER_API_KEY in .env file")
            raise
        except APITimeoutError:
            logger.error("[SERVICE] ❌ TIMEOUT — No response within 30 seconds")
            logger.error("  → Fix: Model may be overloaded, try again later")
            raise
        except APIConnectionError:
            logger.error("[SERVICE] ❌ CONNECTION ERROR — Cannot reach OpenRouter")
            logger.error("  → Fix: Check internet connection")
            raise
        except APIError as e:
            logger.error(f"[SERVICE] ❌ API ERROR — {type(e).__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"[SERVICE] ❌ UNEXPECTED — {type(e).__name__}: {e}")
            raise

    def reset_conversation(self):
        """Clear all conversation history from the database."""
        user = self._get_default_user()
        sessions = self.session_repo.get_sessions_by_user(user.id)
        
        if sessions:
            session_to_delete = sessions[0]
            logger.info(f"[SERVICE] 🗑️ reset_conversation() → deleting session: {session_to_delete.id}")
            self.session_repo.delete_session(session_to_delete.id)
        else:
            logger.info("[SERVICE] 🗑️ reset_conversation() → no active session to reset")

    def get_history(self) -> list[dict]:
        """Return conversation history from the database, excluding the system prompt."""
        user = self._get_default_user()
        session = self._get_or_create_default_session(user.id)
        
        db_messages = self.message_repo.get_messages_by_session(session.id)
        
        # Format for the API response (exclude system prompt for cleaner UI)
        history = [{"role": msg.role, "content": msg.content} for msg in db_messages if msg.role != "system"]
        logger.debug(f"[SERVICE] get_history() → returning {len(history)} messages from DB")
        return history
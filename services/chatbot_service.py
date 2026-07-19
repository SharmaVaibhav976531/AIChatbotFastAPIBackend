# services/chatbot_service.py

import uuid
import logging
import time
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, AuthenticationError
from core.settings import get_settings
from database.repositories import UserRepository, ChatSessionRepository, MessageRepository
from database.models.user import User
from database.models.session import ChatSession
from services.retrieval_service import RetrievalService
from services.rag_service import RAGService

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Core service that communicates with the AI model via OpenRouter.
    This service is STATELESS. It relies entirely on the database for conversation history.
    
    PHASE 7: Integrated with RAGService for complete grounded RAG generation.
    """

    def __init__(
        self, 
        user_repo: UserRepository, 
        session_repo: ChatSessionRepository, 
        message_repo: MessageRepository,
        retrieval_service: RetrievalService | None = None,
        rag_service: RAGService | None = None
    ):
        self.settings = get_settings()
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.openrouter_api_key,
            timeout=30.0,
            max_retries=3,
        )
        self.base_system_prompt = "You are a helpful, concise AI assistant."
        
        # Repositories injected via FastAPI Dependency Injection
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.retrieval_service = retrieval_service
        self.rag_service = rag_service

    # =====================================================================
    # SESSION RESOLUTION
    # =====================================================================
    def _resolve_session(self, user: User, session_id: uuid.UUID | None = None) -> ChatSession:
        """
        Resolve which session to use for the conversation.
        
        Priority:
        1. If session_id is provided → use that specific session (verify ownership)
        2. If no session_id → use the user's latest session
        3. If user has no sessions → create a new one
        
        Args:
            user: The authenticated user
            session_id: Optional specific session to use
            
        Returns:
            ChatSession: The resolved session
            
        Raises:
            ValueError: If session_id is provided but not found or not owned
        """
        if session_id:
            session = self.session_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            if session.user_id != user.id:
                raise ValueError("Access denied to this session")
            return session
        
        # No session_id → get or create latest
        sessions = self.session_repo.get_sessions_by_user(user.id)
        if not sessions:
            logger.info(f"[SERVICE] No active session for user {user.username}. Creating new session...")
            return self.session_repo.create_session(user_id=user.id, title="New Chat")
        return sessions[0]

    # =====================================================================
    # RAG CONTEXT BUILDING
    # =====================================================================
    def _build_rag_prompt(self, user_message: str, user: User, session_id: uuid.UUID | None = None) -> str:
        """
        Build a system prompt augmented with relevant document context for the current session.
        
        If the user has uploaded documents to this specific session and relevant chunks are found,
        they are injected into the system prompt so the LLM can answer based on the session's documents.
        """
        if not self.retrieval_service:
            return self.base_system_prompt
        
        context = self.retrieval_service.retrieve_context(
            query=user_message,
            user_id=user.id,
            session_id=session_id,
            top_k=5,
            similarity_threshold=0.05
        )
        
        if not context:
            return self.base_system_prompt
        
        # Build RAG-augmented prompt
        rag_prompt = (
            f"{self.base_system_prompt}\n\n"
            "You have access to the user's uploaded documents. "
            "Use the following document excerpts to answer the user's question. "
            "If the answer is found in the documents, cite the source filename. "
            "If the documents don't contain relevant information, say so and answer from your general knowledge.\n\n"
            "══════════════════════════════════════\n"
            "DOCUMENT CONTEXT:\n"
            "══════════════════════════════════════\n"
            f"{context}\n"
            "══════════════════════════════════════"
        )
        
        logger.info(f"[SERVICE] 📄 RAG context injected into system prompt for session {session_id} ({len(context)} chars)")
        return rag_prompt

    # =====================================================================
    # CORE BUSINESS LOGIC
    # =====================================================================
    def get_response(self, user_message: str, user: User, session_id: uuid.UUID | None = None) -> str:
        """
        Processes a user message, persists it to DB, loads history, calls the LLM, 
        and persists the AI response.
        
        PHASE 3 CHANGES:
        - Accepts a User object (from JWT auth) instead of creating a "guest"
        - Accepts optional session_id to target a specific session
        """
        func_start = time.time()

        # 1. Resolve Session (using authenticated user)
        session = self._resolve_session(user, session_id)
        logger.info(f"[SERVICE] Processing message for user: {user.username}, session: {session.id}")

        # 2. Save User Message to DB (Done BEFORE calling LLM to prevent data loss on timeout)
        self.message_repo.create_message(
            session_id=session.id,
            role="user",
            content=user_message,
            model_name="N/A"
        )

        # 3. RAG Retrieval — Search uploaded documents in this session for relevant context
        system_prompt = self._build_rag_prompt(user_message, user, session_id=session.id)

        # 4. Load Conversation History from DB
        db_messages = self.message_repo.get_messages_by_session(session.id)
        
        # 5. Format Messages for OpenRouter
        messages = [{"role": "system", "content": system_prompt}]
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

    def reset_conversation(self, user: User):
        """
        Clear the conversation history for the user's latest session.
        
        PHASE 3 CHANGES:
        - Accepts a User object instead of looking up "guest"
        """
        sessions = self.session_repo.get_sessions_by_user(user.id)
        
        if sessions:
            session_to_delete = sessions[0]
            logger.info(f"[SERVICE] 🗑️ reset_conversation() → deleting session: {session_to_delete.id} for user: {user.username}")
            self.session_repo.delete_session(session_to_delete.id)
        else:
            logger.info(f"[SERVICE] 🗑️ reset_conversation() → no active session to reset for user: {user.username}")

    def get_history(self, user: User, session_id: uuid.UUID | None = None) -> list[dict]:
        """
        Return conversation history from the database, excluding the system prompt.
        
        PHASE 3 CHANGES:
        - Accepts a User object instead of looking up "guest"
        - Supports optional session_id parameter
        """
        session = self._resolve_session(user, session_id)
        
        db_messages = self.message_repo.get_messages_by_session(session.id)
        
        # Format for the API response (exclude system prompt for cleaner UI)
        history = [{"role": msg.role, "content": msg.content} for msg in db_messages if msg.role != "system"]
        logger.debug(f"[SERVICE] get_history() → returning {len(history)} messages from DB for user: {user.username}")
        return history
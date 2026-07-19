# services/chatbot_service.py

"""
Orchestrates complete AI chat lifecycle:
Session loading → Multi-Tier Memory → Planner → Tool Router → Tools (Calculator, Python, Search, RAG) →
Executor → Advanced Prompt Assembly → LLM Inference → Message Persistence.
"""

import uuid
import logging
import time
from typing import Optional
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, AuthenticationError
from core.settings import get_settings
from database.repositories import UserRepository, ChatSessionRepository, MessageRepository
from database.models.user import User
from database.models.session import ChatSession
from services.retrieval_service import RetrievalService
from services.rag_service import RAGService
from services.memory_service import MemoryService
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent

from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

EducationalLogger.log_file_execution(
    file_name="services/chatbot_service.py",
    purpose="Orchestrates complete AI agent and chat lifecycle with memory and tool routing.",
    responsibilities=[
        "Resolve active chat session for user",
        "Persist user message to PostgreSQL",
        "Retrieve multi-tiered AI memory",
        "Generate execution plan via PlannerAgent",
        "Route & execute subtasks via ExecutorAgent & ToolRouter",
        "Assemble advanced prompt and invoke LLM API",
        "Persist AI response to PostgreSQL"
    ]
)


class ChatbotService:
    def __init__(
        self, 
        user_repo: UserRepository, 
        session_repo: ChatSessionRepository, 
        message_repo: MessageRepository,
        retrieval_service: RetrievalService | None = None,
        rag_service: RAGService | None = None,
        memory_service: MemoryService | None = None,
        planner_agent: PlannerAgent | None = None,
        executor_agent: ExecutorAgent | None = None
    ):
        self.settings = get_settings()
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.openrouter_api_key,
            timeout=30.0,
            max_retries=3,
        )
        self.base_system_prompt = "You are a helpful, concise AI assistant."
        
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.retrieval_service = retrieval_service
        self.rag_service = rag_service
        self.memory_service = memory_service
        self.planner_agent = planner_agent
        self.executor_agent = executor_agent

    def _resolve_session(self, user: User, session_id: uuid.UUID | None = None) -> ChatSession:
        if session_id:
            session = self.session_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            if session.user_id != user.id:
                raise ValueError("Access denied to this session")
            return session
        
        sessions = self.session_repo.get_sessions_by_user(user.id)
        if not sessions:
            logger.info(f"[SERVICE] No active session for user {user.username}. Creating new session...")
            return self.session_repo.create_session(user_id=user.id, title="New Chat")
        return sessions[0]

    def _build_rag_prompt(self, user_message: str, user: User, session_id: uuid.UUID | None = None) -> str:
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
        
        rag_prompt = (
            f"{self.base_system_prompt}\n\n"
            "Use the following document excerpts to answer the user's question:\n\n"
            f"{context}\n"
        )
        return rag_prompt

    def get_response(self, user_message: str, user: User, session_id: uuid.UUID | None = None) -> str:
        start_time = EducationalLogger.log_function_enter(
            file_name="services/chatbot_service.py",
            class_name="ChatbotService",
            func_name="get_response",
            purpose="Process user message through Agent workflow and return AI response.",
            input_params={"user": user.username, "session_id": session_id, "user_message": f"'{user_message[:30]}...'"}
        )

        # 1. Resolve Session
        session = self._resolve_session(user, session_id)

        # 2. Save User Message to DB
        self.message_repo.create_message(
            session_id=session.id,
            role="user",
            content=user_message,
            model_name="N/A"
        )

        # 3. Retrieve Memory Context (IF ENABLED)
        user_mem = None
        if self.settings.enable_memory and self.memory_service:
            user_mem = self.memory_service.get_user_memory(user.id, session.id)

        # 4. Agent Planning & Execution (IF ENABLED)
        tool_outputs_text = ""
        if self.settings.enable_planner and self.planner_agent and self.executor_agent:
            plan = self.planner_agent.create_plan(user_message)
            tool_results = self.executor_agent.execute_plan(plan, user_id=user.id, session_id=session.id)
            
            tool_outputs = []
            for r in tool_results:
                if r.status == "success" and r.output:
                    tool_outputs.append(f"[{r.tool_name.upper()} OUTPUT]: {r.output}")
            if tool_outputs:
                tool_outputs_text = "\n\n" + "\n".join(tool_outputs)

        # 5. Build System Prompt & Load History
        system_prompt = self._build_rag_prompt(user_message, user, session_id=session.id)
        if tool_outputs_text:
            system_prompt += tool_outputs_text

        db_messages = self.message_repo.get_messages_by_session(session.id)
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})

        EducationalLogger.log_prompt_builder_execution(
            system_prompt_len=len(system_prompt),
            context_len=len(system_prompt) - len(self.base_system_prompt),
            history_count=len(db_messages)
        )

        try:
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
            total_tokens = completion.usage.total_tokens if completion and completion.usage else None
            EducationalLogger.log_openrouter_execution(
                model_name=self.settings.model_name,
                messages_count=len(messages),
                total_tokens=total_tokens,
                duration_ms=round(api_ms, 2)
            )

            if completion and completion.choices:
                reply = completion.choices[0].message.content or ""

                self.message_repo.create_message(
                    session_id=session.id,
                    role="assistant",
                    content=reply,
                    model_name=self.settings.model_name,
                    token_count=total_tokens
                )

                EducationalLogger.log_function_exit("services/chatbot_service.py", "ChatbotService", "get_response", f"reply='{reply[:40]}...'", start_time, "SUCCESS")
                return reply

            EducationalLogger.log_function_exit("services/chatbot_service.py", "ChatbotService", "get_response", "No choices returned", start_time, "FAILED")
            return "[No choices returned by the API]"

        except (APIError, APITimeoutError, APIConnectionError, AuthenticationError) as e:
            EducationalLogger.log_educational_error("services/chatbot_service.py", "get_response", 195, e, user_message, "String reply", "Verify API Key and Network.")
            logger.error(f"[SERVICE] OpenRouter API Error: {e}")
            return f"Error communicating with AI service: {str(e)}"
        except Exception as e:
            EducationalLogger.log_educational_error("services/chatbot_service.py", "get_response", 200, e, user_message, "String reply", "Check system logs.")
            logger.error(f"[SERVICE] Unexpected Error: {e}")
            return f"An unexpected error occurred: {str(e)}"
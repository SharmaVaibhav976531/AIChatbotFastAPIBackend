# services/prompt_builder_service.py

"""
Advanced Prompt Builder Service — Complete RAG & AI Agent Component

Assembles deterministic system prompts incorporating:
System Prompt -> Injected Context -> Conversation History -> User Memory -> Question -> Instructions
"""

import logging
from typing import Dict, Any, List, Optional
from core.settings import get_settings
from schemas.rag import BuiltContext, PromptPayload
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

ADVANCED_GROUNDED_SYSTEM_PROMPT = """You are an enterprise-grade AI Assistant with document grounding and agent tool capabilities.

PROMPT STRUCTURE & INSTRUCTIONS:
1. Primary Source: Use the RETRIEVED DOCUMENT CONTEXT below whenever present to answer the user's question accurately.
2. Grounding Rules: Cite source filenames and page/chunk positions. Do not invent non-existent facts.
3. User Memory & Preferences: Respect the user's preferences and memory facts provided below.
4. Formatting: Output clear, structured responses with markdown formatting.

USER MEMORY & PREFERENCES:
{user_memory_section}

RETRIEVED DOCUMENT CONTEXT:
{retrieved_context}
"""


class PromptBuilderService:
    def __init__(self):
        self.settings = get_settings()

    def build_rag_prompt(
        self,
        query: str,
        built_context: BuiltContext,
        chat_history: list[dict] | None = None,
        user_memory: Dict[str, Any] | None = None
    ) -> PromptPayload:
        """
        Builds an advanced prompt payload with system prompt, memory, context, history, and instructions.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/prompt_builder_service.py",
            class_name="PromptBuilderService",
            func_name="build_rag_prompt",
            purpose="Construct multi-section system prompt and message array for LLM.",
            input_params={"query": f"'{query[:30]}...'", "context_chunks": built_context.chunk_count if built_context else 0}
        )

        has_context = bool(built_context and built_context.context_text.strip())
        ctx_text = built_context.context_text if has_context else "No document context retrieved."

        mem_lines = []
        if user_memory:
            if user_memory.get("preferences"):
                mem_lines.append(f"• Preferences: {user_memory['preferences']}")
            if user_memory.get("session_summary"):
                mem_lines.append(f"• Session Summary: {user_memory['session_summary']}")
        mem_str = "\n".join(mem_lines) if mem_lines else "None recorded."

        system_prompt = ADVANCED_GROUNDED_SYSTEM_PROMPT.format(
            user_memory_section=mem_str,
            retrieved_context=ctx_text
        )

        formatted_messages = [{"role": "system", "content": system_prompt}]

        # Inject Conversation History
        history_tokens = 0
        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    formatted_messages.append({"role": role, "content": content})
                    history_tokens += len(content.split())

        # Append current user query
        formatted_messages.append({"role": "user", "content": query})

        sys_tokens = len(system_prompt.split())
        ctx_tokens = len(ctx_text.split())
        query_tokens = len(query.split())
        total_tokens = sys_tokens + history_tokens + query_tokens

        # Educational Logger breakdown
        EducationalLogger.log_prompt_builder_execution(
            system_prompt_len=len(system_prompt),
            context_len=len(ctx_text),
            history_count=len(chat_history) if chat_history else 0
        )

        EducationalLogger.log_function_exit(
            file_name="services/prompt_builder_service.py",
            class_name="PromptBuilderService",
            func_name="build_rag_prompt",
            returned_value=f"PromptPayload({len(formatted_messages)} msgs, ~{total_tokens} tokens)",
            start_time=start_time
        )

        return PromptPayload(
            system_prompt=system_prompt,
            context_text=ctx_text,
            user_query=query,
            formatted_messages=formatted_messages
        )

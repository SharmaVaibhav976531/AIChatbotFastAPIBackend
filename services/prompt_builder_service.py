# services/prompt_builder_service.py

"""
Phase 7: Prompt Builder Service

Constructs deterministic system prompts and message structures for LLM response generation.
Supports system instructions, context injection, conversation history, and user question positioning.
"""

import logging
from core.settings import get_settings
from schemas.rag import BuiltContext, PromptPayload

logger = logging.getLogger(__name__)

STRICT_GROUNDED_SYSTEM_PROMPT = """You are an accurate, helpful AI Assistant with access to uploaded user documents.

GROUNDING RULES (STRICTLY FOLLOW):
1. Answer the user's question using ONLY the provided RETRIEVED CONTEXT below.
2. Do NOT use outside knowledge or make assumptions beyond what is explicitly stated in the context.
3. If the provided context does NOT contain enough information to answer the question, state clearly:
   "The uploaded documents do not contain enough information to answer this question."
4. Maintain a professional, polite tone.
5. Keep answers clear, concise, and accurate to the document sources.

RETRIEVED DOCUMENT CONTEXT:
{retrieved_context}
"""

UNGROUNDED_FALLBACK_SYSTEM_PROMPT = """You are a helpful, intelligent AI Assistant.
Answer the user's question accurately and concisely using your standard knowledge.
"""


class PromptBuilderService:
    def __init__(self):
        self.settings = get_settings()

    def build_rag_prompt(
        self,
        query: str,
        built_context: BuiltContext,
        chat_history: list[dict] | None = None
    ) -> PromptPayload:
        """
        Builds a grounded system prompt with context injection and conversation history.
        
        Args:
            query: Current user question
            built_context: BuiltContext payload from ContextBuilderService
            chat_history: Prior conversation turns [{role: 'user'|'assistant', content: '...'}]
            
        Returns:
            PromptPayload object ready for OpenAI SDK completion call.
        """
        has_context = bool(built_context and built_context.context_text.strip())

        if has_context:
            system_prompt = STRICT_GROUNDED_SYSTEM_PROMPT.format(
                retrieved_context=built_context.context_text
            )
        else:
            system_prompt = UNGROUNDED_FALLBACK_SYSTEM_PROMPT

        formatted_messages = [{"role": "system", "content": system_prompt}]

        # Inject Conversation History (up to last 10 turns)
        if chat_history:
            for msg in chat_history[-10:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant") and content:
                    formatted_messages.append({"role": role, "content": content})

        # Append current user query
        formatted_messages.append({"role": "user", "content": query})

        logger.info(f"[PROMPT-BUILDER] Assembled prompt with {len(formatted_messages)} messages | Has Context: {has_context}")

        return PromptPayload(
            system_prompt=system_prompt,
            context_text=built_context.context_text if has_context else "",
            user_query=query,
            formatted_messages=formatted_messages
        )

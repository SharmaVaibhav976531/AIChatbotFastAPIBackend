# services/grounding_service.py

"""
Phase 7: Grounding & Relevance Service

Evaluates retrieval results and LLM outputs for grounding confidence,
hallucination prevention, and fallback decisions.
"""

import logging
from core.settings import get_settings
from schemas.rag import BuiltContext

logger = logging.getLogger(__name__)

NO_INFO_STATEMENT = "The uploaded documents do not contain enough information to answer this question."


class GroundingService:
    def __init__(self):
        self.settings = get_settings()

    def should_use_grounded_rag(self, built_context: BuiltContext, query: str) -> tuple[bool, str]:
        """
        Determines whether the retrieved context contains sufficient evidence to attempt grounded generation.
        
        Returns:
            Tuple of (use_rag: bool, reason: str)
        """
        if not self.settings.rag_enabled:
            return False, "RAG feature disabled in settings"

        if not built_context or not built_context.context_text.strip():
            return False, "No retrieved context available"

        if built_context.chunk_count == 0:
            return False, "Zero matching document chunks found above threshold"

        # High-level query intent check (conversational greetings bypass document grounding)
        greetings = {"hi", "hello", "hey", "who are you", "what can you do", "help", "thanks", "thank you"}
        clean_query = query.strip().lower()
        if clean_query in greetings:
            return False, "Conversational greeting query"

        return True, f"Found {built_context.chunk_count} relevant context chunks ({built_context.total_tokens} tokens)"

    def is_hallucinated_response(self, response_text: str) -> bool:
        """
        Checks if LLM response indicates lack of information in context.
        """
        if not response_text:
            return True
        return NO_INFO_STATEMENT.lower() in response_text.lower()

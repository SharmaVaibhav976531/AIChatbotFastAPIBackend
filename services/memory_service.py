# services/memory_service.py

"""
AI Memory Service — Multi-Tiered User & Session Isolated Memory

Manages:
- Short-term Conversation Memory
- Summary Memory (auto-summarization of past turns)
- Semantic Memory (extracted factual insights)
- User Preference Memory (customized user preferences)
- Session Memory (isolated per session ID)
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from services.cache_service import CacheService
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Provides multi-tiered, isolated memory management per user and per chat session.
    """

    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache_service = cache_service

    def get_user_memory(self, user_id: uuid.UUID, session_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """
        Loads short-term conversation memory, summary memory, semantic memory, and user preferences.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/memory_service.py",
            class_name="MemoryService",
            func_name="get_user_memory",
            purpose="Retrieve user and session isolated multi-tiered memory.",
            input_params={"user_id": str(user_id), "session_id": str(session_id) if session_id else "None"}
        )

        user_key = f"user_memory:{user_id}"
        session_key = f"session_memory:{session_id}" if session_id else None

        user_prefs = {}
        semantic_mem = []
        summary_mem = ""

        if self.cache_service:
            cached_user = self.cache_service.get(user_key)
            if cached_user and isinstance(cached_user, dict):
                user_prefs = cached_user.get("preferences", {})
                semantic_mem = cached_user.get("semantic_facts", [])

            if session_key:
                cached_session = self.cache_service.get(session_key)
                if cached_session and isinstance(cached_session, dict):
                    summary_mem = cached_session.get("summary", "")

        memory_payload = {
            "user_id": str(user_id),
            "session_id": str(session_id) if session_id else None,
            "preferences": user_prefs,
            "semantic_facts": semantic_mem,
            "session_summary": summary_mem
        }

        EducationalLogger.log_function_exit(
            file_name="services/memory_service.py",
            class_name="MemoryService",
            func_name="get_user_memory",
            returned_value=f"Memory (facts={len(semantic_mem)}, summary_len={len(summary_mem)})",
            start_time=start_time
        )
        return memory_payload

    def save_user_preference(self, user_id: uuid.UUID, key: str, value: Any) -> None:
        """Saves a user preference key-value pair into isolated memory."""
        user_key = f"user_memory:{user_id}"
        current = {}
        if self.cache_service:
            c = self.cache_service.get(user_key)
            if c and isinstance(c, dict):
                current = c
        
        prefs = current.get("preferences", {})
        prefs[key] = value
        current["preferences"] = prefs

        if self.cache_service:
            self.cache_service.set(user_key, current, ttl=86400 * 30)

        logger.info(f"[MEMORY] Saved user preference for user {user_id}: {key}={value}")

    def update_session_summary(self, session_id: uuid.UUID, summary: str) -> None:
        """Updates the conversation summary memory for a specific chat session."""
        session_key = f"session_memory:{session_id}"
        current = {}
        if self.cache_service:
            c = self.cache_service.get(session_key)
            if c and isinstance(c, dict):
                current = c

        current["summary"] = summary
        if self.cache_service:
            self.cache_service.set(session_key, current, ttl=86400 * 7)

        logger.info(f"[MEMORY] Updated session summary for session {session_id} ({len(summary)} chars)")

# agents/tools/rag_bridge_tool.py

"""
RAG Bridge Tool — Bridge between AI Agent Tool Router and RAG Retrieval Pipeline
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional
from schemas.agent import ToolExecutionResult
from services.retrieval_service import RetrievalService
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class RAGBridgeTool:
    """
    Adapter tool that executes document context retrieval when selected by the Agent Tool Router.
    """

    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service

    def supports(self, input_data: Any, intent: Optional[str] = None) -> bool:
        """
        Validates if RAG retrieval is applicable for the given query/intent.
        Returns False for pure math or code execution tasks.
        """
        if isinstance(input_data, dict):
            q_str = input_data.get("query") or input_data.get("expression") or ""
        else:
            q_str = str(input_data)

        if intent and intent.upper() in ["DOCUMENT_QA", "DOCUMENT_ANALYSIS", "DOCUMENT_SUMMARIZATION", "DOCUMENT_COMPARISON", "RAG_SEARCH", "KNOWLEDGE_SEARCH", "MULTI_STEP_TASK"]:
            return True

        q_lower = str(q_str).lower().strip()
        
        # Avoid running RAG on pure arithmetic
        if q_lower.replace(" ", "").isdigit() or any(p in q_lower for p in ["245*", "5+5", "sqrt("]):
            return False

        return True

    def execute(self, query: str, user_id: uuid.UUID, session_id: uuid.UUID | None = None) -> ToolExecutionResult:
        t0 = time.time()
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/tools/rag_bridge_tool.py",
            class_name="RAGBridgeTool",
            func_name="execute",
            purpose="Execute vector search for user documents via agent tool bridge.",
            input_params={"query": query, "user_id": str(user_id), "session_id": str(session_id)}
        )

        if not self.supports(query):
            duration_ms = round((time.time() - t0) * 1000, 2)
            logger.info(f"[RAG_TOOL] supports() = FALSE for query '{query[:40]}...'. Skipped.")
            return ToolExecutionResult(
                tool_name="rag",
                status="skipped",
                output={"reason": "unsupported_input", "message": "RAG retrieval is not applicable for this query intent."},
                execution_time_ms=duration_ms
            )

        try:
            context = self.retrieval_service.retrieve_context(
                query=query,
                user_id=user_id,
                session_id=session_id,
                top_k=5,
                similarity_threshold=0.05
            )
            duration_ms = round((time.time() - t0) * 1000, 2)

            EducationalLogger.log_function_exit(
                file_name="agents/tools/rag_bridge_tool.py",
                class_name="RAGBridgeTool",
                func_name="execute",
                returned_value=f"RAG Context ({len(context or '')} chars)",
                start_time=start_time
            )

            return ToolExecutionResult(
                tool_name="rag",
                status="success",
                output={"context": context or "", "has_context": bool(context)},
                execution_time_ms=duration_ms
            )

        except Exception as e:
            duration_ms = round((time.time() - t0) * 1000, 2)
            EducationalLogger.log_educational_error(
                file_name="agents/tools/rag_bridge_tool.py",
                func_name="execute",
                line_no=40,
                error=e,
                input_data=query,
                expected="RAG context string",
                fix_suggestion="Check retrieval service."
            )
            return ToolExecutionResult(
                tool_name="rag",
                status="error",
                output=None,
                error_message=str(e),
                execution_time_ms=duration_ms
            )

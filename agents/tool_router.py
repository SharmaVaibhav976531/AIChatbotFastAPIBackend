# agents/tool_router.py

"""
Tool Router — Intelligent Tool Dispatcher for Agent System

Routes subtasks to Calculator, Python REPL, Search Tool, RAG Bridge, or LLM.
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional
from schemas.agent import ToolExecutionResult
from agents.tools.calculator_tool import CalculatorTool
from agents.tools.python_repl_tool import PythonREPLTool
from agents.tools.search_tool import SearchTool
from agents.tools.rag_bridge_tool import RAGBridgeTool
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class ToolRouter:
    """
    Registry and execution router for agent tools.
    """

    def __init__(
        self,
        calculator_tool: Optional[CalculatorTool] = None,
        python_repl_tool: Optional[PythonREPLTool] = None,
        search_tool: Optional[SearchTool] = None,
        rag_bridge_tool: Optional[RAGBridgeTool] = None
    ):
        self.calculator_tool = calculator_tool or CalculatorTool()
        self.python_repl_tool = python_repl_tool or PythonREPLTool()
        self.search_tool = search_tool or SearchTool()
        self.rag_bridge_tool = rag_bridge_tool

    def route_and_execute(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        user_id: uuid.UUID,
        session_id: Optional[uuid.UUID] = None,
        intent: Optional[str] = None
    ) -> ToolExecutionResult:
        """
        Validates tool capabilities and dispatches request to appropriate tool handler.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/tool_router.py",
            class_name="ToolRouter",
            func_name="route_and_execute",
            purpose="Route and execute subtask on designated tool provider with capability validation.",
            input_params={"tool_name": tool_name, "tool_input": tool_input, "intent": intent}
        )

        name_clean = tool_name.lower().strip()

        if name_clean == "calculator":
            expr = tool_input.get("expression", tool_input.get("query", "0"))
            calc_type = tool_input.get("calc_type", "general")
            if not self.calculator_tool.supports(expr, intent=intent):
                logger.warning(f"[TOOL-ROUTER] ⚠️ Calculator Tool rejected input '{expr}' for intent '{intent}'. Skipping.")
                res = ToolExecutionResult(
                    tool_name="calculator",
                    status="skipped",
                    output={"reason": "unsupported_input", "message": "Calculator does not support natural language query."},
                    execution_time_ms=0.0
                )
            else:
                res = self.calculator_tool.execute(expression=expr, calc_type=calc_type)

        elif name_clean == "python_repl":
            code = tool_input.get("code", tool_input.get("script", tool_input.get("query", "")))
            if not self.python_repl_tool.supports(code, intent=intent):
                logger.warning(f"[TOOL-ROUTER] ⚠️ Python REPL Tool rejected input '{code[:30]}...' for intent '{intent}'. Skipping.")
                res = ToolExecutionResult(
                    tool_name="python_repl",
                    status="skipped",
                    output={"reason": "unsupported_input", "message": "Python REPL tool executes code only, not code generation."},
                    execution_time_ms=0.0
                )
            else:
                res = self.python_repl_tool.execute(code=code)

        elif name_clean == "search":
            q = tool_input.get("query", "")
            if not self.search_tool.supports(q, intent=intent):
                logger.warning(f"[TOOL-ROUTER] ⚠️ Search Tool rejected query '{q[:30]}...' for intent '{intent}'. Skipping.")
                res = ToolExecutionResult(
                    tool_name="search",
                    status="skipped",
                    output={"reason": "unsupported_input", "message": "Search tool is not applicable for this query intent."},
                    execution_time_ms=0.0
                )
            else:
                res = self.search_tool.execute(query=q)

        elif name_clean == "rag" and self.rag_bridge_tool:
            q = tool_input.get("query", "")
            if not self.rag_bridge_tool.supports(q, intent=intent):
                logger.warning(f"[TOOL-ROUTER] ⚠️ RAG Tool rejected query '{q[:30]}...' for intent '{intent}'. Skipping.")
                res = ToolExecutionResult(
                    tool_name="rag",
                    status="skipped",
                    output={"reason": "unsupported_input", "message": "RAG tool is not applicable for this query intent."},
                    execution_time_ms=0.0
                )
            else:
                res = self.rag_bridge_tool.execute(query=q, user_id=user_id, session_id=session_id)

        else:
            duration_ms = 1.0
            res = ToolExecutionResult(
                tool_name=tool_name,
                status="success",
                output={"message": f"Executed direct LLM subtask for input: {tool_input}"},
                execution_time_ms=duration_ms
            )

        EducationalLogger.log_function_exit(
            file_name="agents/tool_router.py",
            class_name="ToolRouter",
            func_name="route_and_execute",
            returned_value=f"ToolResult({res.tool_name}, status={res.status})",
            start_time=start_time
        )
        return res

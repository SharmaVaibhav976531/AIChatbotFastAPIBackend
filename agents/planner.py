# agents/planner.py

"""
Planner Agent — Semantic Intent Classification & Multi-Step Task Decomposition

Analyzes user input intent semantically (via LLM / structured classifier) and builds structured multi-step ExecutionPlan.
"""

import json
import re
import time
import logging
from typing import List, Dict, Any
from openai import OpenAI
from core.settings import get_settings
from schemas.agent import ExecutionPlan, PlanStep
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

VALID_INTENT_CATEGORIES = [
    "GENERAL_CHAT", "QUESTION_ANSWERING", "DOCUMENT_QA", "DOCUMENT_ANALYSIS",
    "DOCUMENT_SUMMARIZATION", "DOCUMENT_COMPARISON", "RAG_SEARCH", "KNOWLEDGE_SEARCH",
    "LIVE_SEARCH", "WEB_SEARCH", "MATH", "STATISTICS", "FINANCIAL_CALCULATION",
    "UNIT_CONVERSION", "DATE_TIME", "PYTHON_EXECUTION", "CODE_GENERATION",
    "CODE_EXPLANATION", "CODE_DEBUGGING", "SQL", "IMAGE_ANALYSIS",
    "MULTI_STEP_TASK", "AGENT_TASK", "GENERAL_AI"
]

SYSTEM_PLANNER_PROMPT = """You are a Senior AI Agent Planner & Semantic Intent Classifier.
Analyze the user's query and generate a structured JSON execution plan.

Intent Categories:
- GENERAL_CHAT, QUESTION_ANSWERING, DOCUMENT_QA, DOCUMENT_ANALYSIS, DOCUMENT_SUMMARIZATION, DOCUMENT_COMPARISON
- RAG_SEARCH, KNOWLEDGE_SEARCH, LIVE_SEARCH, WEB_SEARCH
- MATH, STATISTICS, FINANCIAL_CALCULATION, UNIT_CONVERSION, DATE_TIME
- PYTHON_EXECUTION, CODE_GENERATION, CODE_EXPLANATION, CODE_DEBUGGING, SQL, MULTI_STEP_TASK, GENERAL_AI

Available Tools:
- 'calculator': ONLY for pure arithmetic or mathematical formulas (e.g., '245*876', 'sqrt(49)', 'compound interest'). NEVER for natural language text, resume analysis, or comparisons.
- 'search': For real-time web search, current market trends, live news, or external web facts.
- 'rag': For retrieving content from user documents, resumes, PDFs, or session context.
- 'python_repl': ONLY when the user explicitly requests to EXECUTE/RUN Python code in a REPL sandbox. NEVER for writing/explaining code.
- 'llm': For general chat, Q&A, code writing, or synthesizing answers from tool outputs.

Rules:
1. If query requires comparing uploaded documents/resume with current market trends, select 'DOCUMENT_COMPARISON' or 'MULTI_STEP_TASK' with steps: Step 1: 'rag', Step 2: 'search'.
2. If query asks to write or explain code, select 'CODE_GENERATION' with tool 'llm' (DO NOT use 'python_repl').
3. If query asks to run/execute code, select 'PYTHON_EXECUTION' with tool 'python_repl'.
4. If confidence < 0.6 or query is ambiguous, set intent to 'GENERAL_AI' and tool 'llm'.

Output strictly valid JSON in this format:
{
  "intent_category": "<CATEGORY>",
  "confidence": 0.95,
  "required_resources": ["Resume", "Market Trends"],
  "reasoning": "<EXPLANATION>",
  "steps": [
    {
      "step_number": 1,
      "description": "<DESCRIPTION>",
      "tool_name": "<TOOL_NAME>",
      "tool_input": {"query": "<QUERY_OR_EXPRESSION>"}
    }
  ]
}
"""


class PlannerAgent:
    """
    Semantic Planner Agent that classifies user intent using LLM inference
    and constructs ordered ExecutionPlan objects.
    """

    def __init__(self, client: OpenAI | None = None):
        self.settings = get_settings()
        self.client = client or OpenAI(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.base_url
        )

    def create_plan(self, query: str) -> ExecutionPlan:
        """
        Detects query intent semantically and outputs a structured execution plan.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/planner.py",
            class_name="PlannerAgent",
            func_name="create_plan",
            purpose="Analyze query intent semantically and build subtask execution plan.",
            input_params={"query": f"'{query[:40]}...'"}
        )

        plan = None
        # Try LLM semantic planning first
        try:
            plan = self._create_plan_via_llm(query)
        except Exception as e:
            logger.warning(f"[PLANNER] LLM planner failed: {e}. Falling back to semantic pattern classifier.")

        # Fallback to semantic rules if LLM failed or produced unconfident results
        if not plan:
            plan = self._create_fallback_plan(query)

        self._log_planner_decision(plan)

        EducationalLogger.log_function_exit(
            file_name="agents/planner.py",
            class_name="PlannerAgent",
            func_name="create_plan",
            returned_value=f"Plan(intent='{plan.intent_category}', confidence={plan.confidence}, steps={len(plan.steps)})",
            start_time=start_time
        )
        return plan

    def _create_plan_via_llm(self, query: str) -> ExecutionPlan | None:
        response = self.client.chat.completions.create(
            model=self.settings.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PLANNER_PROMPT},
                {"role": "user", "content": f"User Query: {query}"}
            ],
            temperature=0.1,
            max_tokens=500
        )
        raw_content = response.choices[0].message.content or ""
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if not json_match:
            return None

        cleaned_json = re.sub(r'[\x00-\x1F\x7F]', ' ', json_match.group(0))
        data = json.loads(cleaned_json)
        intent = data.get("intent_category", "GENERAL_AI").upper()
        if intent not in VALID_INTENT_CATEGORIES:
            intent = "GENERAL_AI"

        confidence = float(data.get("confidence", 0.9))
        if confidence < 0.6:
            intent = "GENERAL_AI"

        steps = []
        raw_steps = data.get("steps", [])
        for idx, s in enumerate(raw_steps, start=1):
            t_name = s.get("tool_name", "llm").lower()
            if t_name not in ["calculator", "search", "rag", "python_repl", "llm"]:
                t_name = "llm"
            steps.append(PlanStep(
                step_number=idx,
                description=s.get("description", "Subtask execution"),
                tool_name=t_name,
                tool_input=s.get("tool_input", {"query": query})
            ))

        if not steps:
            steps.append(PlanStep(step_number=1, description="Direct completion", tool_name="llm", tool_input={"query": query}))

        return ExecutionPlan(
            user_query=query,
            intent_category=intent,
            confidence=confidence,
            required_resources=data.get("required_resources", []),
            reasoning=data.get("reasoning", "Semantic plan generated via LLM."),
            steps=steps,
            estimated_steps=len(steps)
        )

    def _create_fallback_plan(self, query: str) -> ExecutionPlan:
        q_clean = query.strip()
        q_lower = q_clean.lower()
        steps: List[PlanStep] = []

        # Check 1: Pure math expression or compound interest
        is_pure_math = bool(re.match(r'^[0-9\s\+\-\*\/\%\^\(\)\.\,]+$', q_clean)) or (
            any(w in q_lower for w in ["sqrt", "sin", "cos", "tan", "log", "factorial", "compound interest"]) and 
            not any(nl in q_lower for nl in ["compare", "resume", "python", "fastapi", "news", "summarize", "write", "explain", "code"])
        )
        if is_pure_math:
            return ExecutionPlan(
                user_query=query,
                intent_category="MATH",
                confidence=0.98,
                required_resources=["Math Evaluator"],
                reasoning="Query represents pure arithmetic or math calculation.",
                steps=[PlanStep(step_number=1, description="Evaluate math formula", tool_name="calculator", tool_input={"expression": query})],
                estimated_steps=1
            )

        # Check 2: Explicit Python REPL code execution request
        is_python_exec = (
            any(phrase in q_lower for phrase in ["execute python", "run python", "run script", "execute code", "run code"]) or 
            ("execute" in q_lower and ("python" in q_lower or "script" in q_lower or "code" in q_lower)) or
            "import pandas" in q_lower or "import numpy" in q_lower
        ) and not any(phrase in q_lower for phrase in ["write python", "write code", "how to write", "explain code"])
        if is_python_exec:
            return ExecutionPlan(
                user_query=query,
                intent_category="PYTHON_EXECUTION",
                confidence=0.95,
                required_resources=["Python REPL Sandbox"],
                reasoning="User explicitly requested Python code execution.",
                steps=[PlanStep(step_number=1, description="Execute Python code", tool_name="python_repl", tool_input={"code": query})],
                estimated_steps=1
            )

        # Check 3: Multi-step Document + Search Comparison
        is_compare = "compare" in q_lower and ("resume" in q_lower or "document" in q_lower or "pdf" in q_lower)
        is_market = any(w in q_lower for w in ["market", "trend", "latest", "news", "job", "salary"])
        if is_compare and is_market:
            return ExecutionPlan(
                user_query=query,
                intent_category="DOCUMENT_COMPARISON",
                confidence=0.96,
                required_resources=["Resume Document", "Market Information"],
                reasoning="Multi-step task requiring internal RAG document retrieval and live market web search.",
                steps=[
                    PlanStep(step_number=1, description="Retrieve document context", tool_name="rag", tool_input={"query": query}),
                    PlanStep(step_number=2, description="Search latest market data", tool_name="search", tool_input={"query": query})
                ],
                estimated_steps=2
            )

        # Check 4: RAG Document Retrieval Only
        if any(w in q_lower for w in ["document", "pdf", "resume", "file", "upload", "knowledge base"]):
            return ExecutionPlan(
                user_query=query,
                intent_category="DOCUMENT_QA",
                confidence=0.92,
                required_resources=["Document Storage"],
                reasoning="Query asks for information contained in uploaded documents.",
                steps=[PlanStep(step_number=1, description="Retrieve document context", tool_name="rag", tool_input={"query": query})],
                estimated_steps=1
            )

        # Check 5: Web Search Only
        if any(w in q_lower for w in ["search", "news", "latest", "current", "internet", "google", "web"]):
            return ExecutionPlan(
                user_query=query,
                intent_category="LIVE_SEARCH",
                confidence=0.90,
                required_resources=["Web Search Engine"],
                reasoning="Query requests real-time web or news information.",
                steps=[PlanStep(step_number=1, description="Execute web search", tool_name="search", tool_input={"query": query})],
                estimated_steps=1
            )

        # Default: General AI / Direct LLM Completion
        return ExecutionPlan(
            user_query=query,
            intent_category="GENERAL_AI",
            confidence=0.85,
            required_resources=["LLM Inference Engine"],
            reasoning="Query is general knowledge or conversational.",
            steps=[PlanStep(step_number=1, description="Direct LLM response", tool_name="llm", tool_input={"query": query})],
            estimated_steps=1
        )

    def _log_planner_decision(self, plan: ExecutionPlan) -> None:
        tools_selected = [s.tool_name for s in plan.steps]
        all_tools = ["calculator", "search", "rag", "python_repl", "llm"]
        tools_rejected = [t for t in all_tools if t not in tools_selected]
        order_str = " → ".join([f"Step {s.step_number}: {s.tool_name}" for s in plan.steps])

        logger.info(
            f"\n[PLANNER DECISION]\n"
            f"  Detected Intent   : {plan.intent_category}\n"
            f"  Confidence        : {plan.confidence}\n"
            f"  Reason            : {plan.reasoning}\n"
            f"  Selected Tools    : {tools_selected}\n"
            f"  Rejected Tools    : {tools_rejected}\n"
            f"  Execution Order   : {order_str}"
        )

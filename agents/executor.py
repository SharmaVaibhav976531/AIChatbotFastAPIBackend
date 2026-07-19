# agents/executor.py

"""
Executor Agent — Multi-Step Plan Execution & Output Aggregation

Executes steps from an ExecutionPlan sequentially or in parallel using ToolRouter.
Handles retries and merges outputs.
"""

import uuid
import time
import logging
from typing import List, Dict, Any, Optional
from schemas.agent import ExecutionPlan, ToolExecutionResult
from agents.tool_router import ToolRouter
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Executes an ExecutionPlan using ToolRouter, aggregates step outputs, and handles retries.
    """

    def __init__(self, tool_router: ToolRouter):
        self.tool_router = tool_router

    def execute_plan(
        self,
        plan: ExecutionPlan,
        user_id: uuid.UUID,
        session_id: Optional[uuid.UUID] = None
    ) -> List[ToolExecutionResult]:
        """
        Runs plan steps sequentially and returns execution results.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/executor.py",
            class_name="ExecutorAgent",
            func_name="execute_plan",
            purpose="Execute multi-step plan through designated tools.",
            input_params={"intent": plan.intent_category, "step_count": len(plan.steps)}
        )

        results: List[ToolExecutionResult] = []

        for step in plan.steps:
            t0 = time.time()
            step.status = "running"

            res = self.tool_router.route_and_execute(
                tool_name=step.tool_name,
                tool_input=step.tool_input,
                user_id=user_id,
                session_id=session_id,
                intent=plan.intent_category
            )

            step.status = res.status
            step.result = res
            results.append(res)

            if res.status == "skipped":
                logger.info(f"[EXECUTOR] Step {step.step_number} ({step.tool_name}) skipped ({res.output.get('reason', 'unsupported')}). Continuing remaining plan steps.")

        EducationalLogger.log_function_exit(
            file_name="agents/executor.py",
            class_name="ExecutorAgent",
            func_name="execute_plan",
            returned_value=f"Completed {len(results)} tool step executions",
            start_time=start_time
        )
        return results

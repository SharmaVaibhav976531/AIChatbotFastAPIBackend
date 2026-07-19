# schemas/agent.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID


class ToolCallRequest(BaseModel):
    """Payload representing a single tool execution request within a plan step."""
    tool_name: str = Field(..., description="Name of the tool to execute (e.g. calculator, python_repl, rag, database, search)")
    tool_input: Dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to the tool")
    reasoning: Optional[str] = Field(None, description="Rationale for choosing this tool")


class ToolExecutionResult(BaseModel):
    """Output payload resulting from executing a specific tool."""
    tool_name: str = Field(..., description="Name of the executed tool")
    status: str = Field(..., description="Execution status: 'success' or 'error'")
    output: Any = Field(..., description="Raw or formatted tool output data")
    error_message: Optional[str] = Field(None, description="Error detail if status is 'error'")
    execution_time_ms: float = Field(0.0, description="Duration of tool execution in milliseconds")


class PlanStep(BaseModel):
    """A single discrete step in an agent's multi-step plan."""
    step_number: int = Field(..., description="Sequential step index starting from 1")
    description: str = Field(..., description="Human-readable description of what this step accomplishes")
    tool_name: str = Field(..., description="Tool designated for this step")
    tool_input: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the tool")
    status: str = Field("pending", description="Status: pending, running, completed, failed")
    result: Optional[ToolExecutionResult] = Field(None, description="Execution result once completed")


class ExecutionPlan(BaseModel):
    """Structured plan produced by the Planner Node prior to tool execution."""
    user_query: str = Field(..., description="Original user prompt")
    intent_category: str = Field("general", description="Categorized user intent")
    steps: List[PlanStep] = Field(default_factory=list, description="Ordered list of steps to execute")
    estimated_steps: int = Field(0, description="Total number of planned steps")
    confidence: float = Field(1.0, description="Confidence score of intent classification")
    required_resources: List[str] = Field(default_factory=list, description="Resources required for plan")
    reasoning: Optional[str] = Field(None, description="Reasoning behind plan creation")


class AgentDebugResponse(BaseModel):
    """Diagnostic response for /agent/debug and /agent/plan inspection endpoints."""
    user_id: UUID = Field(..., description="Authenticated user ID")
    session_id: UUID = Field(..., description="Active session ID")
    query: str = Field(..., description="Original query")
    intent: str = Field(..., description="Identified intent")
    plan: ExecutionPlan = Field(..., description="Generated execution plan")
    tool_executions: List[ToolExecutionResult] = Field(default_factory=list, description="List of executed tool outputs")
    final_answer: str = Field(..., description="Final aggregated response")
    total_latency_ms: float = Field(0.0, description="Total execution latency in milliseconds")

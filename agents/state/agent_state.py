# agents/state/agent_state.py

from typing import TypedDict, List, Dict, Any, Optional
from uuid import UUID


class AgentState(TypedDict):
    """
    LangGraph State Schema representing state passed through graph nodes.
    Maintains strict user and session isolation.
    """
    user_id: UUID
    session_id: UUID
    query: str
    intent: str
    plan: Optional[Dict[str, Any]]
    current_step_index: int
    steps: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    memory_context: List[Dict[str, str]]
    rag_context: Optional[str]
    final_answer: Optional[str]
    is_completed: bool
    error: Optional[str]
    telemetry: Dict[str, Any]

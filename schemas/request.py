# schemas/request.py
# ══════════════════════════════════════════════════════════════════
# REQUEST SCHEMAS — Input validation for chat endpoints
# ══════════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Request schema for the /chat endpoint.
    
    PHASE 3 CHANGES:
    - Added optional session_id field. If provided, the message is sent
      to that specific session. If omitted, the user's latest session is used.
    """
    # Field(...) means it's required. min_length=1 prevents empty messages.
    message: str = Field(..., min_length=1, max_length=4000, description="The user's message to the chatbot")
    session_id: UUID | None = Field(
        None,
        description="Target session ID. If not provided, the latest session is used."
    )
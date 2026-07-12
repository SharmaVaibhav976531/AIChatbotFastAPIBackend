# schemas/request.py

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    # Field(...) means it's required. min_length=1 prevents empty messages.
    message: str = Field(..., min_length=1, max_length=4000, description="The user's message to the chatbot")
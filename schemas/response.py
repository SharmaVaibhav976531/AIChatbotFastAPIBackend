# schemas/response.py

from pydantic import BaseModel
from typing import List, Dict

class ChatResponse(BaseModel):
    reply: str
    model: str

class HealthResponse(BaseModel):
    status: str

class HistoryResponse(BaseModel):
    history: List[Dict[str, str]]
# schemas/document.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    original_filename: str
    extension: str
    file_size: int
    status: str
    created_at: datetime

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
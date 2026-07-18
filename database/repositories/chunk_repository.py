import logging
from sqlalchemy.orm import Session
from database.models.chunk import DocumentChunk

logger = logging.getLogger(__name__)

class ChunkRepository:
    def __init__(self, db: Session): self.db = db

    def create_chunks(self, chunks_data: list[dict]) -> list[DocumentChunk]:
        chunks = [DocumentChunk(**data) for data in chunks_data]
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks: self.db.refresh(chunk)
        return chunks
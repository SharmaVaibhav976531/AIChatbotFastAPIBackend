import logging
from sqlalchemy.orm import Session
from database.models.embedding import Embedding

logger = logging.getLogger(__name__)

class EmbeddingRepository:
    def __init__(self, db: Session): self.db = db

    def create_embeddings(self, embeddings_data: list[dict]):
        records = [Embedding(**data) for data in embeddings_data]
        self.db.add_all(records)
        self.db.commit()
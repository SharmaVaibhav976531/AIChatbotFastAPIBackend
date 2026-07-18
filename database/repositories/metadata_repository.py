import logging
from sqlalchemy.orm import Session
from database.models.chunk_metadata import ChunkMetadata

logger = logging.getLogger(__name__)

class MetadataRepository:
    def __init__(self, db: Session): self.db = db

    def create_metadata(self, metadata_data: list[dict]):
        records = [ChunkMetadata(**data) for data in metadata_data]
        self.db.add_all(records)
        self.db.commit()
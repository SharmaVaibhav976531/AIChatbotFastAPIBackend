# database/repositories/search_repository.py

"""
Phase 6: Search Repository

Data Access Layer for retrieving document chunks and chunk metadata
by document ID, with user ownership verification.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from database.models.chunk import DocumentChunk
from database.models.chunk_metadata import ChunkMetadata
from database.models.document import Document

logger = logging.getLogger(__name__)


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_chunks_by_document(
        self, 
        document_id: uuid.UUID, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[DocumentChunk]:
        """
        Fetches chunks for a given document belonging to the user.
        """
        doc = self.db.query(Document).filter(
            Document.id == document_id, 
            Document.user_id == user_id
        ).first()
        
        if not doc:
            return []

        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_metadata_by_document(
        self, 
        document_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> list[dict]:
        """
        Fetches metadata associated with all chunks of a specific document.
        """
        doc = self.db.query(Document).filter(
            Document.id == document_id, 
            Document.user_id == user_id
        ).first()
        
        if not doc:
            return []

        results = (
            self.db.query(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.chunk_index,
                ChunkMetadata.heading,
                ChunkMetadata.section,
                ChunkMetadata.page_number,
                ChunkMetadata.source,
                ChunkMetadata.language,
                ChunkMetadata.keywords
            )
            .join(ChunkMetadata, ChunkMetadata.chunk_id == DocumentChunk.id)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

        output = []
        for r in results:
            output.append({
                "chunk_id": r.chunk_id,
                "chunk_index": r.chunk_index,
                "heading": r.heading,
                "section": r.section,
                "page_number": r.page_number,
                "source": r.source,
                "language": r.language,
                "keywords": r.keywords
            })
        return output

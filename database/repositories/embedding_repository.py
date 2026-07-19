# database/repositories/embedding_repository.py

import uuid
import logging
from sqlalchemy.orm import Session, joinedload
from database.models.embedding import Embedding
from database.models.chunk import DocumentChunk
from database.models.document import Document

logger = logging.getLogger(__name__)


class EmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_embeddings(self, embeddings_data: list[dict]):
        records = [Embedding(**data) for data in embeddings_data]
        self.db.add_all(records)
        self.db.commit()

    def search_similar(
        self, 
        query_vector: list[float], 
        user_id: uuid.UUID, 
        session_id: uuid.UUID | None = None,
        top_k: int = 5,
        similarity_threshold: float = 0.05
    ) -> list[dict]:
        """
        Perform cosine similarity search on the embeddings table.
        
        Only returns chunks belonging to COMPLETED documents owned by the given user
        and associated with the given chat session (if session_id provided).
        Uses pgvector's cosine distance operator (<=>).
        
        Args:
            query_vector: The embedding vector for the user's query
            user_id: Only search documents belonging to this user
            session_id: Optional session ID filter for chat-isolated document context
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (0-1, higher = more similar)
            
        Returns:
            List of dicts with chunk content, similarity score, and source metadata
        """
        # pgvector cosine distance: 0 = identical, 2 = opposite
        # Cosine similarity = 1 - cosine_distance
        cosine_distance = Embedding.vector.cosine_distance(query_vector)
        
        query = (
            self.db.query(
                DocumentChunk.content,
                DocumentChunk.chunk_index,
                Document.original_filename,
                Document.id.label("document_id"),
                cosine_distance.label("distance")
            )
            .join(DocumentChunk, Embedding.chunk_id == DocumentChunk.id)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(
                Document.user_id == user_id,
                Document.status == "COMPLETED"
            )
        )

        if session_id:
            query = query.filter(Document.session_id == session_id)

        results = query.order_by(cosine_distance.asc()).limit(top_k).all()

        # Convert to dicts and filter by threshold
        similar_chunks = []
        for row in results:
            similarity = 1.0 - row.distance  # Convert distance to similarity
            if similarity >= similarity_threshold:
                similar_chunks.append({
                    "content": row.content,
                    "chunk_index": row.chunk_index,
                    "filename": row.original_filename,
                    "document_id": str(row.document_id),
                    "similarity": round(similarity, 4)
                })

        logger.info(
            f"[RETRIEVAL] Found {len(similar_chunks)}/{len(results)} chunks "
            f"above threshold {similarity_threshold} for user {user_id}"
        )
        return similar_chunks
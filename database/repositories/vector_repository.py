# database/repositories/vector_repository.py

"""
Phase 6: Vector Repository

Data Access Layer for pgvector similarity search operations.
Supports Cosine Similarity, L2 (Euclidean) Distance, and Inner Product metrics
with dynamic SQL-level metadata filtering and strict user ownership isolation.
"""

import uuid
import logging
from typing import Literal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_

from database.models.embedding import Embedding
from database.models.chunk import DocumentChunk
from database.models.document import Document
from database.models.chunk_metadata import ChunkMetadata
from schemas.search import MetadataFilter

logger = logging.getLogger(__name__)


class VectorRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_vectors(
        self,
        query_vector: list[float],
        user_id: uuid.UUID,
        top_k: int = 5,
        similarity_threshold: float = 0.05,
        metric: Literal["cosine", "l2", "inner_product"] = "cosine",
        filters: MetadataFilter | None = None
    ) -> list[dict]:
        """
        Executes pgvector similarity search with metadata filtering and user security scope.
        
        Args:
            query_vector: Dense floating point query embedding vector
            user_id: Authenticated user ID (ensures isolation)
            top_k: Number of nearest candidate chunks to retrieve
            similarity_threshold: Minimum calculated similarity score threshold
            metric: Distance metric algorithm ("cosine", "l2", "inner_product")
            filters: Dynamic metadata filter criteria
            
        Returns:
            List of dictionaries containing chunk details, scores, and source metadata.
        """
        # 1. Select distance expression based on metric
        if metric == "l2":
            dist_expr = Embedding.vector.l2_distance(query_vector)
            order_by_clause = dist_expr.asc()
        elif metric == "inner_product":
            # Inner product in pgvector uses negative inner product operator (<#>)
            dist_expr = Embedding.vector.max_inner_product(query_vector)
            order_by_clause = dist_expr.asc()
        else:
            # Default: Cosine Distance (<=>)
            dist_expr = Embedding.vector.cosine_distance(query_vector)
            order_by_clause = dist_expr.asc()

        # 2. Base Query Joins
        query = (
            self.db.query(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.content,
                DocumentChunk.chunk_index,
                DocumentChunk.token_count,
                Document.id.label("document_id"),
                Document.original_filename,
                dist_expr.label("raw_distance")
            )
            .join(DocumentChunk, Embedding.chunk_id == DocumentChunk.id)
            .join(Document, DocumentChunk.document_id == Document.id)
            .outerjoin(ChunkMetadata, ChunkMetadata.chunk_id == DocumentChunk.id)
            .filter(
                Document.user_id == user_id,
                Document.status == "COMPLETED"
            )
        )

        # 3. Dynamic Metadata Filters
        if filters:
            if filters.document_ids:
                query = query.filter(Document.id.in_(filters.document_ids))
            if filters.filenames:
                query = query.filter(Document.original_filename.in_(filters.filenames))
            if filters.extensions:
                query = query.filter(Document.extension.in_(filters.extensions))
            if filters.mime_types:
                query = query.filter(Document.mime_type.in_(filters.mime_types))
            if filters.created_after:
                query = query.filter(Document.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(Document.created_at <= filters.created_before)
            if filters.min_token_count is not None:
                query = query.filter(DocumentChunk.token_count >= filters.min_token_count)
            if filters.max_token_count is not None:
                query = query.filter(DocumentChunk.token_count <= filters.max_token_count)

        # 4. Order and Limit
        results = query.order_by(order_by_clause).limit(top_k * 2).all()

        # 5. Calculate normalized similarity score & apply score threshold
        ranked_items = []
        rank_counter = 1

        for row in results:
            dist = float(row.raw_distance)
            
            # Convert raw distance to standardized similarity score [0.0 - 1.0]
            if metric == "l2":
                # L2 distance range: [0, inf) -> similarity = 1 / (1 + l2_dist)
                similarity = 1.0 / (1.0 + dist)
            elif metric == "inner_product":
                # Max inner product returns negative dot product in pgvector
                # Negative inner product: -dot_product -> similarity = max(0, -dist)
                similarity = max(0.0, -dist)
            else:
                # Cosine distance range: [0, 2] -> similarity = 1 - cosine_dist
                similarity = 1.0 - dist

            if similarity >= similarity_threshold:
                # Fetch metadata dict if exists
                chunk_meta = None
                meta_obj = self.db.query(ChunkMetadata).filter(ChunkMetadata.chunk_id == row.chunk_id).first()
                if meta_obj:
                    chunk_meta = {
                        "heading": meta_obj.heading,
                        "section": meta_obj.section,
                        "page_number": meta_obj.page_number,
                        "source": meta_obj.source,
                        "language": meta_obj.language,
                        "keywords": meta_obj.keywords
                    }

                ranked_items.append({
                    "rank": rank_counter,
                    "score": round(similarity, 6),
                    "distance": round(dist, 6),
                    "chunk_id": row.chunk_id,
                    "document_id": row.document_id,
                    "filename": row.original_filename,
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                    "token_count": row.token_count,
                    "metadata": chunk_meta
                })
                rank_counter += 1

                if len(ranked_items) >= top_k:
                    break

        logger.info(
            f"[VECTOR-REPO] Search metric='{metric}' top_k={top_k} threshold={similarity_threshold} | "
            f"Retrieved {len(ranked_items)} matching chunks for user {user_id}"
        )
        return ranked_items

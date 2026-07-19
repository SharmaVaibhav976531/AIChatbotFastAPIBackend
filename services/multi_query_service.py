# services/multi_query_service.py

"""
Multi-Query Retrieval Service — Advanced RAG Component

Executes independent vector searches across multiple query variations,
merges retrieved document chunks, deduplicates by chunk ID, and ranks by similarity.
"""

import uuid
import time
import logging
from typing import List, Dict, Any
from database.repositories.embedding_repository import EmbeddingRepository
from services.embedding_service import EmbeddingService
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class MultiQueryService:
    """
    Executes parallel or sequential vector similarity searches for multiple query variations
    and merges the candidate chunk sets with deduplication and score normalization.
    """

    def __init__(self, embedding_repo: EmbeddingRepository, embedding_service: EmbeddingService):
        self.embedding_repo = embedding_repo
        self.embedding_service = embedding_service

    def execute_multi_query_search(
        self,
        queries: List[str],
        user_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        top_k_per_query: int = 4,
        similarity_threshold: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Runs vector search for each query in queries, merges and deduplicates results.
        """
        start_time = EducationalLogger.log_function_enter(
            file_name="services/multi_query_service.py",
            class_name="MultiQueryService",
            func_name="execute_multi_query_search",
            purpose="Execute multi-query vector searches, merge results, and rank candidates.",
            input_params={"query_count": len(queries), "user_id": str(user_id), "session_id": str(session_id)}
        )

        t0 = time.time()
        chunk_map: Dict[str, Dict[str, Any]] = {}
        query_embeddings = self.embedding_service.generate_embeddings(queries)

        for idx, (q, q_vec) in enumerate(zip(queries, query_embeddings), 1):
            chunks = self.embedding_repo.search_similar(
                query_vector=q_vec,
                user_id=user_id,
                session_id=session_id,
                top_k=top_k_per_query,
                similarity_threshold=similarity_threshold
            )

            for chunk in chunks:
                chunk_key = f"{chunk['document_id']}:{chunk['chunk_index']}"
                if chunk_key not in chunk_map:
                    chunk_map[chunk_key] = chunk
                else:
                    # If already retrieved, keep highest similarity score
                    if chunk["similarity"] > chunk_map[chunk_key]["similarity"]:
                        chunk_map[chunk_key] = chunk

        merged_chunks = list(chunk_map.values())
        merged_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        duration_ms = round((time.time() - t0) * 1000, 2)

        EducationalLogger.log_rag_step(
            step_num=3,
            step_name="Multi-Query Vector Retrieval",
            why_needed="Perform parallel search across all query variations to maximize document recall.",
            input_data=f"Queries ({len(queries)}): {queries[:2]}...",
            output_data=f"Merged & Deduplicated Chunks ({len(merged_chunks)})",
            duration_ms=duration_ms
        )

        EducationalLogger.log_function_exit(
            file_name="services/multi_query_service.py",
            class_name="MultiQueryService",
            func_name="execute_multi_query_search",
            returned_value=f"List of {len(merged_chunks)} merged chunks",
            start_time=start_time
        )
        return merged_chunks

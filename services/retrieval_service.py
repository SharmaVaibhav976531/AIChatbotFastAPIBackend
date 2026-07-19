# services/retrieval_service.py

"""
RAG Retrieval Service — The bridge between uploaded documents and the chatbot.

This service:
1. Embeds the user's chat query using the same embedding model
2. Searches pgvector for the most similar document chunks
3. Formats the results as context for the LLM's system prompt
"""

import uuid
import time
import logging
from database.repositories.embedding_repository import EmbeddingRepository
from services.embedding_service import EmbeddingService

from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

# Log file execution details for architecture learning
EducationalLogger.log_file_execution(
    file_name="services/retrieval_service.py",
    purpose="Retrieval Service bridging document embeddings with RAG prompt context construction.",
    responsibilities=[
        "Generate vector embedding for user query",
        "Perform similarity search on PostgreSQL pgvector via EmbeddingRepository",
        "Format retrieved chunks with source filenames and similarity scores for LLM prompt injection"
    ]
)


class RetrievalService:
    def __init__(self, embedding_repo: EmbeddingRepository, embedding_service: EmbeddingService):
        self.embedding_repo = embedding_repo
        self.embedding_service = embedding_service

    def retrieve_context(
        self,
        query: str,
        user_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        top_k: int = 5,
        similarity_threshold: float = 0.05
    ) -> str | None:
        start_time = EducationalLogger.log_function_enter(
            file_name="services/retrieval_service.py",
            class_name="RetrievalService",
            func_name="retrieve_context",
            purpose="Embed query and retrieve top relevant document chunks for active chat session.",
            input_params={"query": f"'{query[:30]}...'", "user_id": str(user_id), "session_id": str(session_id) if session_id else "None"}
        )
        try:
            EducationalLogger.log_rag_pipeline_banner(query=query, session_id=str(session_id) if session_id else None)

            # 1. Embed the user's query
            emb_start = time.time()
            EducationalLogger.log_function_intent(
                target_func="EmbeddingService.generate_embeddings",
                reason="Convert natural language query into vector embedding.",
                input_desc=f"text='{query[:30]}...'",
                expected_output="List of float vectors"
            )
            query_vectors = self.embedding_service.generate_embeddings([query])
            emb_ms = round((time.time() - emb_start) * 1000, 2)
            
            if not query_vectors:
                EducationalLogger.log_function_exit("services/retrieval_service.py", "RetrievalService", "retrieve_context", "None (Embedding Failed)", start_time, "FAILED")
                return None
            
            query_vector = query_vectors[0]
            EducationalLogger.log_rag_step(1, "Embedding Generation", "Convert user query into vector space for similarity comparison", f"'{query[:30]}...'", f"Vector dim={len(query_vector)}", emb_ms)

            # 2. Search for similar chunks in the user's session documents
            search_start = time.time()
            EducationalLogger.log_function_intent(
                target_func="EmbeddingRepository.search_similar",
                reason="Query pgvector for chunks matching embedding in session context.",
                input_desc=f"vector_dim={len(query_vector)}, top_k={top_k}, session_id={session_id}",
                expected_output="List of matching chunk dicts"
            )
            similar_chunks = self.embedding_repo.search_similar(
                query_vector=query_vector,
                user_id=user_id,
                session_id=session_id,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            search_ms = round((time.time() - search_start) * 1000, 2)
            EducationalLogger.log_rag_step(2, "Vector Search", "Find top-K nearest document chunks in database", f"Top-K={top_k}", f"Retrieved {len(similar_chunks)} chunks", search_ms)

            if not similar_chunks:
                EducationalLogger.log_function_exit("services/retrieval_service.py", "RetrievalService", "retrieve_context", "None (No Chunks Found)", start_time, "SUCCESS")
                return None

            # 3. Format the context for the LLM
            context_parts = []
            for i, chunk in enumerate(similar_chunks, 1):
                context_parts.append(
                    f"[Source {i}: {chunk['filename']} (relevance: {chunk['similarity']:.0%})]\n"
                    f"{chunk['content']}"
                )

            context = "\n\n---\n\n".join(context_parts)
            EducationalLogger.log_function_exit("services/retrieval_service.py", "RetrievalService", "retrieve_context", f"Context string ({len(context)} chars)", start_time, "SUCCESS")
            return context

        except Exception as e:
            EducationalLogger.log_educational_error("services/retrieval_service.py", "retrieve_context", 114, e, query, "Formatted context string", "Verify database connection and embedding model output.")
            logger.error(f"[RETRIEVAL] ❌ Error during retrieval: {e}")
            # Don't crash the chat — just proceed without context
            return None

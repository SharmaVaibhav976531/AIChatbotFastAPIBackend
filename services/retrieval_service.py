# services/retrieval_service.py

"""
RAG Retrieval Service — The bridge between uploaded documents and the chatbot.

This service:
1. Embeds the user's chat query using the same embedding model
2. Searches pgvector for the most similar document chunks
3. Formats the results as context for the LLM's system prompt
"""

import uuid
import logging
from database.repositories.embedding_repository import EmbeddingRepository
from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


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
        """
        Retrieve relevant document context for a user's chat query.
        
        Args:
            query: The user's message
            user_id: The authenticated user's ID
            session_id: Optional session ID to isolate document context per chat
            top_k: Max number of chunks to retrieve
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            Formatted context string to inject into the LLM prompt, 
            or None if no relevant documents found.
        """
        try:
            # 1. Embed the user's query
            logger.info(f"[RETRIEVAL] Embedding query: '{query[:80]}...' (session: {session_id})")
            query_vectors = self.embedding_service.generate_embeddings([query])
            
            if not query_vectors:
                logger.warning("[RETRIEVAL] Failed to generate query embedding")
                return None
            
            query_vector = query_vectors[0]

            # 2. Search for similar chunks in the user's session documents
            similar_chunks = self.embedding_repo.search_similar(
                query_vector=query_vector,
                user_id=user_id,
                session_id=session_id,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )

            if not similar_chunks:
                logger.info("[RETRIEVAL] No relevant document chunks found")
                return None

            # 3. Format the context for the LLM
            context_parts = []
            for i, chunk in enumerate(similar_chunks, 1):
                context_parts.append(
                    f"[Source {i}: {chunk['filename']} (relevance: {chunk['similarity']:.0%})]\n"
                    f"{chunk['content']}"
                )

            context = "\n\n---\n\n".join(context_parts)
            
            logger.info(
                f"[RETRIEVAL] ✅ Retrieved {len(similar_chunks)} chunks | "
                f"Best match: {similar_chunks[0]['similarity']:.0%} from {similar_chunks[0]['filename']}"
            )
            
            return context

        except Exception as e:
            logger.error(f"[RETRIEVAL] ❌ Error during retrieval: {e}")
            # Don't crash the chat — just proceed without context
            return None

# services/rag_service.py

"""
Phase 7: Complete RAG Pipeline Orchestration Service

Orchestrates the entire RAG workflow:
Query Embedding → Vector Search → Re-ranking → Context Assembly → Prompt Building →
LLM Generation → Grounded Response → Source Attribution.
"""

import time
import json
import uuid
import logging
from typing import Any
from openai import AsyncOpenAI

from core.settings import get_settings
from services.vector_search_service import VectorSearchService
from services.reranking_service import RerankingService
from services.context_builder_service import ContextBuilderService
from services.grounding_service import GroundingService
from services.prompt_builder_service import PromptBuilderService
from services.cache_service import CacheService
from schemas.rag import RAGResponse, BuiltContext
from schemas.search import MetadataFilter, VectorSearchRequest

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(
        self,
        vector_search_service: VectorSearchService,
        reranking_service: RerankingService,
        context_builder_service: ContextBuilderService,
        grounding_service: GroundingService,
        prompt_builder_service: PromptBuilderService,
        cache_service: CacheService | None = None
    ):
        self.settings = get_settings()
        self.vector_search_service = vector_search_service
        self.reranking_service = reranking_service
        self.context_builder_service = context_builder_service
        self.grounding_service = grounding_service
        self.prompt_builder_service = prompt_builder_service
        self.cache_service = cache_service
        
        # Initialize OpenAI Async Client for LLM generation
        self.client = AsyncOpenAI(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.base_url
        )

    async def execute_rag(
        self,
        user_id: uuid.UUID,
        query: str,
        session_id: uuid.UUID | None = None,
        chat_history: list[dict] | None = None,
        top_k: int | None = None,
        threshold: float | None = None,
        filters: MetadataFilter | None = None,
        request_id: str | None = None
    ) -> RAGResponse:
        """
        Executes complete RAG pipeline for a given user query with session context isolation.
        """
        pipeline_start = time.time()
        req_id = request_id or str(uuid.uuid4())[:8]

        logger.info(f"[RAG-PIPELINE][{req_id}] Starting RAG execution for user={user_id} | session={session_id} | query='{query}'")

        # Ensure filters includes session_id if provided
        target_filters = filters or MetadataFilter()
        if session_id and not target_filters.session_id:
            target_filters.session_id = session_id

        # 1. Redis Cache Check (Prompt & Response Cache) scoped by user_id AND session_id
        cache_key = f"rag_resp:{user_id}:{session_id or 'all'}:{hash(query)}"
        if self.cache_service and self.settings.search_cache_enabled:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.info(f"[RAG-PIPELINE][{req_id}] ⚡ Redis Prompt Cache Hit! (session: {session_id})")
                try:
                    resp_dict = json.loads(cached_data)
                    resp_dict["total_latency_ms"] = round((time.time() - pipeline_start) * 1000, 2)
                    return RAGResponse(**resp_dict)
                except Exception as cache_err:
                    logger.warning(f"[RAG-PIPELINE][{req_id}] Failed to parse cached RAG response: {cache_err}")

        # 2. Step 1: Vector Search
        search_start = time.time()
        search_response = await self.vector_search_service.search(
            user_id=user_id,
            query=query,
            top_k=top_k or self.settings.max_context_chunks,
            similarity_threshold=threshold or self.settings.default_similarity_threshold,
            filters=target_filters
        )
        search_latency = round((time.time() - search_start) * 1000, 2)

        # 3. Step 2: Re-ranking Layer
        rerank_start = time.time()
        reranked_chunks, rerank_latency = self.reranking_service.rerank(
            candidates=search_response.results,
            query=query
        )

        # 4. Step 3: Context Builder
        built_context: BuiltContext = self.context_builder_service.build_context(
            reranked_chunks=reranked_chunks
        )

        # 5. Step 4: Grounding Policy Decision
        use_rag, grounding_reason = self.grounding_service.should_use_grounded_rag(
            built_context=built_context,
            query=query
        )
        logger.info(f"[RAG-PIPELINE][{req_id}] Grounding Decision: use_rag={use_rag} ({grounding_reason})")

        # 6. Step 5: Prompt Assembly
        prompt_payload = self.prompt_builder_service.build_rag_prompt(
            query=query,
            built_context=built_context if use_rag else BuiltContext(context_text="", total_tokens=0, chunk_count=0, sources=[]),
            chat_history=chat_history
        )

        # 7. Step 6: LLM Response Generation
        gen_start = time.time()
        fallback_used = False
        try:
            completion = await self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=prompt_payload.formatted_messages,
                temperature=0.2 if use_rag else 0.7,
                max_tokens=1000
            )
            answer_text = completion.choices[0].message.content or ""
        except Exception as llm_err:
            logger.error(f"[RAG-PIPELINE][{req_id}] LLM Generation failed: {llm_err}")
            answer_text = "I encountered an error generating an answer. Please try again."
            fallback_used = True

        gen_latency = round((time.time() - gen_start) * 1000, 2)

        # Check if response indicates no document information found
        if use_rag and self.grounding_service.is_hallucinated_response(answer_text):
            logger.info(f"[RAG-PIPELINE][{req_id}] Response indicated insufficient context information.")

        total_latency = round((time.time() - pipeline_start) * 1000, 2)

        rag_response = RAGResponse(
            answer=answer_text,
            is_grounded=use_rag,
            fallback_used=fallback_used,
            sources=built_context.sources if use_rag else [],
            context_tokens=built_context.total_tokens if use_rag else 0,
            total_latency_ms=total_latency,
            search_latency_ms=search_latency,
            rerank_latency_ms=rerank_latency,
            generation_latency_ms=gen_latency
        )

        # 8. Redis Prompt Cache Write
        if self.cache_service and self.settings.search_cache_enabled and use_rag:
            try:
                await self.cache_service.set(
                    cache_key,
                    rag_response.model_dump_json(),
                    ttl=self.settings.prompt_cache_ttl
                )
            except Exception as cache_write_err:
                logger.warning(f"[RAG-PIPELINE][{req_id}] Failed to write RAG response to Redis cache: {cache_write_err}")

        logger.info(
            f"[RAG-PIPELINE][{req_id}] Completed RAG Execution | Total Latency: {total_latency}ms | "
            f"Search: {search_latency}ms | Rerank: {rerank_latency}ms | LLM Gen: {gen_latency}ms"
        )

        return rag_response

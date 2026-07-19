# services/rag_service.py

"""
Phase 7 & 8: Complete Advanced RAG Pipeline Orchestration Service

Orchestrates:
Query Expansion → HyDE → Multi-Query Vector Search → Parent-Child Expansion →
Re-ranking → Context Compression → Context Assembly → Prompt Building →
LLM Generation → Citations & Source Attribution.
"""

import time
import json
import uuid
import logging
from typing import Any, List
from openai import AsyncOpenAI

from core.settings import get_settings
from services.vector_search_service import VectorSearchService
from services.reranking_service import RerankingService
from services.context_builder_service import ContextBuilderService
from services.grounding_service import GroundingService
from services.prompt_builder_service import PromptBuilderService
from services.cache_service import CacheService
from services.query_expansion_service import QueryExpansionService
from services.hyde_service import HyDEService
from services.multi_query_service import MultiQueryService
from services.parent_child_service import ParentChildService
from services.context_compression_service import ContextCompressionService
from services.citation_service import CitationService
from schemas.rag import RAGResponse, BuiltContext
from schemas.search import MetadataFilter, VectorSearchRequest
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(
        self,
        vector_search_service: VectorSearchService,
        reranking_service: RerankingService,
        context_builder_service: ContextBuilderService,
        grounding_service: GroundingService,
        prompt_builder_service: PromptBuilderService,
        cache_service: CacheService | None = None,
        query_expansion_service: QueryExpansionService | None = None,
        hyde_service: HyDEService | None = None,
        multi_query_service: MultiQueryService | None = None,
        parent_child_service: ParentChildService | None = None,
        context_compression_service: ContextCompressionService | None = None
    ):
        self.settings = get_settings()
        self.vector_search_service = vector_search_service
        self.reranking_service = reranking_service
        self.context_builder_service = context_builder_service
        self.grounding_service = grounding_service
        self.prompt_builder_service = prompt_builder_service
        self.cache_service = cache_service
        
        self.query_expansion_service = query_expansion_service or QueryExpansionService()
        self.hyde_service = hyde_service or HyDEService()
        self.multi_query_service = multi_query_service or MultiQueryService(
            embedding_repo=vector_search_service.embedding_repo,
            embedding_service=vector_search_service.embedding_service
        )
        self.parent_child_service = parent_child_service
        self.context_compression_service = context_compression_service or ContextCompressionService()

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
        Executes complete Advanced RAG pipeline for a user query.
        """
        pipeline_start = time.time()
        req_id = request_id or str(uuid.uuid4())[:8]

        EducationalLogger.log_rag_pipeline_banner(query=query, session_id=str(session_id) if session_id else None)

        target_filters = filters or MetadataFilter()
        if session_id and not target_filters.session_id:
            target_filters.session_id = session_id

        # 1. Redis Cache Check
        cache_key = f"rag_resp:{user_id}:{session_id or 'all'}:{hash(query)}"
        if self.cache_service and self.settings.search_cache_enabled:
            cached_data = self.cache_service.get(cache_key)
            if cached_data:
                logger.info(f"[RAG-PIPELINE][{req_id}] ⚡ Redis Prompt Cache Hit!")
                try:
                    resp_dict = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                    resp_dict["total_latency_ms"] = round((time.time() - pipeline_start) * 1000, 2)
                    return RAGResponse(**resp_dict)
                except Exception as cache_err:
                    logger.warning(f"[RAG-PIPELINE][{req_id}] Failed to parse cached RAG response: {cache_err}")

        queries_to_search = [query]

        # 2. Step 1: Query Expansion (IF ENABLED)
        if self.settings.enable_query_expansion:
            exp_res = self.query_expansion_service.expand_query(query, max_variations=self.settings.max_multi_queries)
            queries_to_search = exp_res.expanded_queries

        # 3. Step 2: HyDE Passage Generation (IF ENABLED)
        if self.settings.enable_hyde:
            hyde_res = self.hyde_service.generate_hypothetical_document(query)
            if hyde_res.hypothetical_document and hyde_res.hypothetical_document != query:
                queries_to_search.append(hyde_res.hypothetical_document)

        # 4. Step 3: Vector Retrieval (Multi-Query / Standard)
        search_start = time.time()
        if self.settings.enable_multi_query and len(queries_to_search) > 1:
            raw_chunks = self.multi_query_service.execute_multi_query_search(
                queries=queries_to_search,
                user_id=user_id,
                session_id=session_id,
                top_k_per_query=top_k or self.settings.max_context_chunks,
                similarity_threshold=threshold or self.settings.default_similarity_threshold
            )
        else:
            search_req = VectorSearchRequest(
                query=query,
                session_id=session_id,
                top_k=top_k or self.settings.max_context_chunks,
                similarity_threshold=threshold or self.settings.default_similarity_threshold,
                filters=target_filters
            )
            search_response = self.vector_search_service.search(
                request=search_req,
                user_id=user_id
            )
            raw_chunks = [r.model_dump() for r in search_response.results]
        search_latency = round((time.time() - search_start) * 1000, 2)

        # 5. Step 4: Parent-Child Context Expansion (IF ENABLED & DB session available)
        if self.settings.enable_parent_child and self.parent_child_service:
            raw_chunks = self.parent_child_service.expand_to_parent_context(raw_chunks)

        # 6. Step 5: Re-ranking
        rerank_start = time.time()
        reranked_chunks, rerank_latency = self.reranking_service.rerank(
            candidates=raw_chunks,
            query=query
        )

        # 7. Step 6: Context Compression (IF ENABLED)
        candidate_dicts = [c.model_dump() if hasattr(c, "model_dump") else c for c in reranked_chunks]
        if self.settings.enable_context_compression and candidate_dicts:
            candidate_dicts = self.context_compression_service.compress_chunks(
                candidate_dicts, target_ratio=self.settings.compression_ratio
            )

        # 8. Step 7: Context Assembly & Grounding Decision
        built_context: BuiltContext = self.context_builder_service.build_context(
            reranked_chunks=candidate_dicts
        )

        use_rag, grounding_reason = self.grounding_service.should_use_grounded_rag(
            built_context=built_context,
            query=query
        )

        # 9. Step 8: Citations & Source Attribution
        sources, citations, citation_footer = CitationService.build_sources_and_citations(candidate_dicts)

        # 10. Step 9: Advanced Prompt Assembly
        prompt_payload = self.prompt_builder_service.build_rag_prompt(
            query=query,
            built_context=built_context if use_rag else BuiltContext(context_text="", total_tokens=0, chunk_count=0, sources=[]),
            chat_history=chat_history
        )

        # 11. Step 10: LLM Response Generation
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

        # Append citations footer if enabled
        if use_rag and self.settings.enable_citations and citation_footer:
            answer_text += citation_footer

        total_latency = round((time.time() - pipeline_start) * 1000, 2)

        rag_response = RAGResponse(
            answer=answer_text,
            is_grounded=use_rag,
            fallback_used=fallback_used,
            sources=sources if use_rag else [],
            context_tokens=built_context.total_tokens if use_rag else 0,
            total_latency_ms=total_latency,
            search_latency_ms=search_latency,
            rerank_latency_ms=rerank_latency,
            generation_latency_ms=gen_latency
        )

        # 12. Redis Cache Store
        if self.cache_service and self.settings.search_cache_enabled and use_rag:
            try:
                self.cache_service.set(
                    cache_key,
                    rag_response.model_dump_json(),
                    ttl=self.settings.prompt_cache_ttl
                )
            except Exception as cache_write_err:
                logger.warning(f"[RAG-PIPELINE][{req_id}] Failed to write RAG response to Redis: {cache_write_err}")

        return rag_response

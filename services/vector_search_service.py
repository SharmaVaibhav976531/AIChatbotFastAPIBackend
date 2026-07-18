# services/vector_search_service.py

"""
Phase 6: Vector Search Service

Primary Orchestration Service for Production Vector Search.
Combines query embedding generation, pgvector vector search execution,
Redis caching, Prometheus latency tracking, and candidate ranking.
"""

import uuid
import time
import json
import logging
from typing import Literal

from core.settings import get_settings
from database.repositories.vector_repository import VectorRepository
from services.embedding_service import EmbeddingService
from services.ranking_service import RankingService
from services.cache_service import CacheService
from schemas.search import VectorSearchRequest, SearchResponse, RankedChunkResult

logger = logging.getLogger(__name__)


class VectorSearchService:
    def __init__(
        self,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
        cache_service: CacheService | None = None
    ):
        self.settings = get_settings()
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service
        self.cache_service = cache_service
        self.ranking_service = RankingService()

    def search(
        self,
        request: VectorSearchRequest,
        user_id: uuid.UUID
    ) -> SearchResponse:
        """
        Executes vector similarity search workflow:
        1. Checks Redis cache (if enabled and requested)
        2. Embeds natural language query string
        3. Queries pgvector via VectorRepository
        4. Ranks candidate results
        5. Writes to Redis cache
        6. Returns structured SearchResponse
        """
        start_time = time.time()
        
        top_k = request.top_k or self.settings.default_top_k
        similarity_threshold = (
            request.similarity_threshold 
            if request.similarity_threshold is not None 
            else self.settings.default_similarity_threshold
        )
        metric = request.distance_metric or self.settings.vector_distance_metric

        # Cache key formulation
        cache_key = None
        if self.cache_service and self.settings.search_cache_enabled and request.use_cache:
            cache_key = f"search:{user_id}:{hash((request.query, top_k, similarity_threshold, metric, str(request.filters)))}"
            cached_data = self.cache_service.get(cache_key)
            if cached_data:
                logger.info(f"[SEARCH-SERVICE] ⚡ Search Cache HIT for query: '{request.query[:50]}'")
                latency_ms = round((time.time() - start_time) * 1000, 2)
                
                # Parse cached dictionary into SearchResponse
                cached_dict = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                cached_dict["latency_ms"] = latency_ms
                cached_dict["cache_hit"] = True
                return SearchResponse(**cached_dict)

        logger.info(f"[SEARCH-SERVICE] 🔍 Search Cache MISS — Executing vector search for query: '{request.query[:50]}'")

        # 1. Embed query text
        query_vectors = self.embedding_service.generate_embeddings([request.query])
        if not query_vectors:
            logger.warning("[SEARCH-SERVICE] ⚠️ Failed to generate embedding for query")
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return SearchResponse(
                query=request.query,
                total_found=0,
                distance_metric=metric,
                search_strategy=self.settings.search_strategy,
                latency_ms=latency_ms,
                cache_hit=False,
                results=[]
            )
        
        query_vector = query_vectors[0]

        # 2. Query pgvector Repository
        raw_candidates = self.vector_repo.search_vectors(
            query_vector=query_vector,
            user_id=user_id,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metric=metric,
            filters=request.filters
        )

        # 3. Rank Candidates
        ranked_results = self.ranking_service.rank_candidates(raw_candidates, top_k=top_k)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        response = SearchResponse(
            query=request.query,
            total_found=len(ranked_results),
            distance_metric=metric,
            search_strategy=self.settings.search_strategy,
            latency_ms=latency_ms,
            cache_hit=False,
            results=ranked_results
        )

        # 4. Save to Redis Cache
        if self.cache_service and cache_key and self.settings.search_cache_enabled:
            try:
                self.cache_service.set(
                    key=cache_key,
                    value=response.model_dump_json(),
                    ttl=self.settings.search_cache_ttl
                )
            except Exception as cache_err:
                logger.warning(f"[SEARCH-SERVICE] Failed to write to search cache: {cache_err}")

        logger.info(
            f"[SEARCH-SERVICE] ✅ Completed vector search | Found {len(ranked_results)} chunks | "
            f"Latency: {latency_ms}ms | Metric: {metric}"
        )
        return response

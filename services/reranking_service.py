# services/reranking_service.py

"""
Phase 7: Re-ranking Service

Dedicated Re-ranking layer for candidate context refinement.
Implements lightweight score and metadata quality reranking to select
the highest quality context chunks before context assembly.
Extensible for future Cross-Encoder, Cohere Rerank, and BGE Reranker models.
"""

import time
import logging
from core.settings import get_settings
from schemas.search import RankedChunkResult
from schemas.rag import RerankedResult

logger = logging.getLogger(__name__)


class RerankingService:
    def __init__(self):
        self.settings = get_settings()

    def rerank(
        self, 
        candidates: list[RankedChunkResult], 
        query: str,
        max_chunks: int | None = None
    ) -> tuple[list[RerankedResult], float]:
        """
        Reranks retrieved candidate chunks based on similarity score and metadata quality signals.
        
        Args:
            candidates: List of RankedChunkResult items from vector search
            query: User's query string for keyword intersection checks
            max_chunks: Maximum top chunks to select post-reranking
            
        Returns:
            Tuple of (list of RerankedResult, reranking latency in ms)
        """
        start_time = time.time()
        max_select = max_chunks or self.settings.max_context_chunks

        if not candidates:
            return [], 0.0

        if not self.settings.enable_reranking:
            # Bypass reranking: direct conversion preserving vector search rank
            results = []
            for item in candidates[:max_select]:
                results.append(
                    RerankedResult(
                        original_rank=item.rank,
                        new_rank=item.rank,
                        initial_score=item.score,
                        reranked_score=item.score,
                        chunk_id=item.chunk_id,
                        document_id=item.document_id,
                        filename=item.filename,
                        content=item.content,
                        token_count=item.token_count or len(item.content.split()),
                        metadata=item.metadata
                    )
                )
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return results, latency_ms

        query_terms = set(query.lower().split())
        scored_items = []

        for item in candidates:
            base_score = item.score
            bonus = 0.0
            
            meta = item.metadata or {}
            
            # 1. Heading / Section presence bonus
            if meta.get("heading") or meta.get("section"):
                bonus += 0.02
                
            # 2. Page number presence bonus
            if meta.get("page_number") is not None:
                bonus += 0.01

            # 3. Query keyword overlap bonus
            content_words = set(item.content.lower().split())
            overlap = query_terms.intersection(content_words)
            if overlap:
                bonus += min(0.05, len(overlap) * 0.01)

            final_score = round(base_score + bonus, 6)

            scored_items.append({
                "candidate": item,
                "initial_score": base_score,
                "final_score": final_score
            })

        # Sort descending by final_score
        sorted_scored = sorted(scored_items, key=lambda x: x["final_score"], reverse=True)

        reranked_results = []
        for new_idx, entry in enumerate(sorted_scored[:max_select], 1):
            cand = entry["candidate"]
            reranked_results.append(
                RerankedResult(
                    original_rank=cand.rank,
                    new_rank=new_idx,
                    initial_score=entry["initial_score"],
                    reranked_score=entry["final_score"],
                    chunk_id=cand.chunk_id,
                    document_id=cand.document_id,
                    filename=cand.filename,
                    content=cand.content,
                    token_count=cand.token_count or len(cand.content.split()),
                    metadata=cand.metadata
                )
            )

        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[RERANKER] Reranked {len(candidates)} candidates → selected top {len(reranked_results)} | Latency: {latency_ms}ms")
        return reranked_results, latency_ms

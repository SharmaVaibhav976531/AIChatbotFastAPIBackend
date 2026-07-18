# services/ranking_service.py

"""
Phase 6: Ranking Service

Sorts, ranks, and formats candidate search results into standardized RankedChunkResult items.
Prepared for future Reciprocal Rank Fusion (RRF) and Cross-Encoder re-ranking in Phase 7.
"""

import logging
from schemas.search import RankedChunkResult

logger = logging.getLogger(__name__)


class RankingService:
    @staticmethod
    def rank_candidates(candidate_items: list[dict], top_k: int = 5) -> list[RankedChunkResult]:
        """
        Sorts candidates by similarity score in descending order and formats into RankedChunkResult models.
        """
        # Sort by score descending
        sorted_candidates = sorted(candidate_items, key=lambda x: x["score"], reverse=True)
        
        results = []
        for rank_idx, item in enumerate(sorted_candidates[:top_k], 1):
            results.append(
                RankedChunkResult(
                    rank=rank_idx,
                    score=item["score"],
                    distance=item["distance"],
                    chunk_id=item["chunk_id"],
                    document_id=item["document_id"],
                    filename=item["filename"],
                    chunk_index=item["chunk_index"],
                    content=item["content"],
                    token_count=item.get("token_count"),
                    metadata=item.get("metadata")
                )
            )
        return results

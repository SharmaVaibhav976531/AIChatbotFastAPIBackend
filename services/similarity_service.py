# services/similarity_service.py

"""
Phase 6: Similarity Service

Encapsulates distance score calculation, unit normalization, and threshold filtering logic.
"""

import math
import logging

logger = logging.getLogger(__name__)


class SimilarityService:
    @staticmethod
    def calculate_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """
        Calculates cosine similarity between two float vectors.
        Returns a float between -1.0 and 1.0 (1.0 = identical).
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    @staticmethod
    def distance_to_similarity(distance: float, metric: str = "cosine") -> float:
        """
        Converts raw distance score to normalized similarity score [0.0 - 1.0].
        """
        if metric == "l2":
            return 1.0 / (1.0 + distance)
        elif metric == "inner_product":
            return max(0.0, -distance)
        else:
            # Cosine distance: similarity = 1 - cosine_distance
            return 1.0 - distance

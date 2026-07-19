# services/embedding_service.py

import math
import time
from abc import ABC, abstractmethod
from openai import OpenAI
from core.settings import get_settings
import httpx
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# pgvector hard limit: both HNSW and IVFFlat indexes support max 2000 dimensions.
# Embeddings exceeding this limit will be truncated and re-normalized.
MAX_INDEXABLE_DIMENSIONS = 2000

# =====================================================================
# EMBEDDING MODEL REGISTRY
# =====================================================================
# Centralized registry to validate configured models against expected dimensions.
SUPPORTED_EMBEDDING_MODELS = {
    "nomic-ai/nomic-embed-text-v1.5": 768,
    "thenlper/gte-base": 768,
    "BAAI/bge-base-en-v1.5": 768,
    "BAAI/bge-large-en-v1.5": 1024,
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "jinaai/jina-embeddings-v2-base-en": 768,
    "nvidia/nemotron-3-embed-1b:free": 2048,  # Native 2048, truncated to <=2000 for pgvector
}

# =====================================================================
# STRATEGY PATTERN: Embedding Provider Abstraction
# =====================================================================
class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass

# =====================================================================
# CONCRETE IMPLEMENTATION: OpenAI Compatible Provider
# =====================================================================
class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        
        # Validate configured dimension against registry
        expected_dim = SUPPORTED_EMBEDDING_MODELS.get(self.model)
        if expected_dim and settings.vector_dimension > expected_dim:
            # Configured dimension is LARGER than what the model outputs — this will fail
            logger.warning(
                f"[EMBEDDING] ⚠️ Dimension mismatch warning: "
                f"Model '{self.model}' outputs {expected_dim} dimensions, "
                f"but VECTOR_DIMENSION is set to {settings.vector_dimension}. "
                f"Update VECTOR_DIMENSION to {expected_dim} or lower."
            )
        elif expected_dim and settings.vector_dimension < expected_dim:
            # Configured dimension is smaller — embeddings will be truncated (this is fine)
            logger.info(
                f"[EMBEDDING] ℹ️ Truncation enabled: "
                f"Model '{self.model}' outputs {expected_dim} dims → "
                f"will be truncated to {settings.vector_dimension} dims "
                f"(pgvector index limit: {MAX_INDEXABLE_DIMENSIONS})"
            )
            
        logger.info(
            f"[EMBEDDING] Initialized provider | "
            f"Model: {self.model} | "
            f"Base URL: {base_url} | "
            f"Configured Dim: {settings.vector_dimension}"
        )

    def _embed_via_raw_http(self, batch: list[str]) -> tuple[list[list[float]], str]:
        """Fallback: Use raw HTTP to avoid OpenAI SDK parsing issues."""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": batch}

        with httpx.Client(timeout=120.0) as http_client:
            resp = http_client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        items = data.get("data", [])
        if not items:
            raise ValueError(f"No embedding data returned from {self.model}")

        items.sort(key=lambda x: x.get("index", 0))
        embeddings = [item["embedding"] for item in items]
        response_model = data.get("model", self.model)
        
        return embeddings, response_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        
        all_embeddings = []
        batch_size = 100
        actual_model_used = self.model
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(
                f"[EMBEDDING] Processing batch {batch_num} | "
                f"Size: {len(batch)} | Model: {self.model}"
            )
            
            try:
                # Primary method: raw HTTP (OpenRouter's embedding response format
                # is incompatible with the OpenAI SDK's parser, so we use direct HTTP).
                batch_embeddings, actual_model_used = self._embed_via_raw_http(batch)
                all_embeddings.extend(batch_embeddings)
                
            except Exception as http_err:
                # Fallback: try the OpenAI SDK in case raw HTTP fails
                logger.warning(
                    f"[EMBEDDING] Raw HTTP failed for batch {batch_num} ({http_err}). "
                    f"Falling back to OpenAI SDK."
                )
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
                    all_embeddings.extend(batch_embeddings)
                    
                    if hasattr(response, 'model') and response.model:
                        actual_model_used = response.model
                except Exception as sdk_err:
                    logger.error(f"[EMBEDDING] ❌ Both methods failed for batch {batch_num}: HTTP={http_err}, SDK={sdk_err}")
                    raise

        # =====================================================================
        # CRITICAL VALIDATION & TRUNCATION
        # =====================================================================
        if all_embeddings:
            actual_dimension = len(all_embeddings[0])
            configured_dimension = settings.vector_dimension
            
            logger.info(
                f"[EMBEDDING] Generated {len(all_embeddings)} embeddings | "
                f"Returned Dim: {actual_dimension} | "
                f"Configured Dim: {configured_dimension} | "
                f"Actual Model: {actual_model_used}"
            )
            
            # If the model returns more dimensions than configured,
            # truncate and re-normalize (Matryoshka-style dimensionality reduction).
            # This is required because pgvector indexes have a 2000-dim hard limit.
            if actual_dimension > configured_dimension:
                logger.info(
                    f"[EMBEDDING] 🔧 Truncating embeddings from {actual_dimension} → {configured_dimension} dims "
                    f"(pgvector index limit: {MAX_INDEXABLE_DIMENSIONS})"
                )
                all_embeddings = self._truncate_and_normalize(all_embeddings, configured_dimension)
            elif actual_dimension < configured_dimension:
                error_msg = (
                    f"Embedding dimension too small!\n"
                    f"  Configured Model: {self.model}\n"
                    f"  Actual Model Used: {actual_model_used}\n"
                    f"  Expected Dimension: {configured_dimension}\n"
                    f"  Returned Dimension: {actual_dimension}\n\n"
                    f"Reason: The model returned fewer dimensions than configured. "
                    f"Update VECTOR_DIMENSION in .env to {actual_dimension}."
                )
                logger.error(f"[EMBEDDING] ❌ {error_msg}")
                raise ValueError(error_msg)
            
            logger.info(
                f"[EMBEDDING] ✅ Final output: {len(all_embeddings)} embeddings × {len(all_embeddings[0])} dims"
            )
                
        return all_embeddings

    @staticmethod
    def _truncate_and_normalize(embeddings: list[list[float]], target_dim: int) -> list[list[float]]:
        """Truncate embeddings to target_dim and L2-normalize.
        
        This is a well-known technique (Matryoshka Representation Learning)
        that preserves most of the semantic information in the leading dimensions.
        """
        result = []
        for vec in embeddings:
            truncated = vec[:target_dim]
            # L2 normalize to maintain unit-length vectors for cosine similarity
            norm = math.sqrt(sum(x * x for x in truncated))
            if norm > 0:
                truncated = [x / norm for x in truncated]
            result.append(truncated)
        return result


# =====================================================================
# SERVICE FACADE
# =====================================================================
embedding_provider = OpenAICompatibleEmbeddingProvider(
    api_key=settings.embedding_api_key,
    base_url=settings.embedding_base_url,
    model=settings.embedding_model
)

from utils.educational_logger import EducationalLogger

class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider = embedding_provider):
        self.provider = provider

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        start_time = EducationalLogger.log_function_enter(
            file_name="services/embedding_service.py",
            class_name="EmbeddingService",
            func_name="generate_embeddings",
            purpose="Generate vector embeddings for input text strings.",
            input_params={"chunks_count": len(texts)}
        )
        t0 = time.time()
        logger.info(f"[EMBEDDING-SERVICE] Generating embeddings for {len(texts)} chunks...")
        vectors = self.provider.embed_documents(texts)
        duration_ms = round((time.time() - t0) * 1000, 2)
        
        if vectors:
            raw_dim = len(vectors[0])
            EducationalLogger.log_embedding_execution(
                model_name=settings.embedding_model,
                input_count=len(texts),
                dimensions=raw_dim,
                duration_ms=duration_ms
            )

        EducationalLogger.log_function_exit(
            file_name="services/embedding_service.py",
            class_name="EmbeddingService",
            func_name="generate_embeddings",
            returned_value=f"List of {len(vectors)} vectors (dim={len(vectors[0]) if vectors else 0})",
            start_time=start_time
        )
        return vectors
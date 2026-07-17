# services/embedding_service.py
from abc import ABC, abstractmethod
from openai import OpenAI
from core.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# =====================================================================
# STRATEGY PATTERN: Embedding Provider Abstraction
# =====================================================================
class EmbeddingProvider(ABC):
    """
    Abstract Base Class for embedding generation.
    Allows seamless swapping between OpenAI, OpenRouter, Ollama, or local models.
    """
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass


# =====================================================================
# CONCRETE IMPLEMENTATION: OpenAI Compatible Provider
# =====================================================================
class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    """
    Generates embeddings using any OpenAI-compatible API.
    Includes batching to prevent API timeouts and memory spikes.
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        logger.info(f"[EMBEDDING] Initialized provider with model: {model} at {base_url}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        
        all_embeddings = []
        batch_size = 100  # Safe batch size for most API providers
        
        # Process in batches to ensure stability for large documents
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.debug(f"[EMBEDDING] Processing batch {i//batch_size + 1} ({len(batch)} chunks)")
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # CRITICAL: Sort by index to ensure the output order exactly matches the input order
                batch_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"[EMBEDDING] ❌ API call failed for batch {i//batch_size + 1}: {e}")
                raise  # Let the Celery task handle the retry logic

        return all_embeddings


# =====================================================================
# SERVICE FACADE
# =====================================================================
# Initialize the provider (Singleton)
embedding_provider = OpenAICompatibleEmbeddingProvider(
    api_key=settings.embedding_api_key,
    base_url=settings.embedding_base_url,
    model=settings.embedding_model
)

class EmbeddingService:
    """
    Facade for embedding generation.
    Orchestrates the provider and handles logging/metrics.
    """
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        logger.info(f"[EMBEDDING-SERVICE] Generating embeddings for {len(texts)} chunks...")
        
        vectors = self.provider.embed_documents(texts)
        
        dimension = len(vectors[0]) if vectors else 0
        logger.info(f"[EMBEDDING-SERVICE] ✅ Generated {len(vectors)} embeddings of dimension {dimension}.")
        
        return vectors
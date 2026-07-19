# core/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import computed_field, model_validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Pydantic V2 configuration for loading .env files
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Environment variables
    openrouter_api_key: str
    model_name: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    base_url: str = "https://openrouter.ai/api/v1"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    frequency_penalty: float = 0.2

    # --- Database Configuration ---
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "chatbot_db"
    database_user: str = "postgres"
    database_password: str = "postgres"

    # --- JWT Authentication Configuration ---
    jwt_secret_key: str = "change-me-in-production"
    jwt_refresh_secret_key: str = "change-me-in-production-refresh"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- Phase 4: Redis & Celery Configuration ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0
    redis_url: str = "redis://localhost:6379/0"
    
    # --- CELERY CONFIGURATION ---
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # --- CACHE CONFIGURATION ---
    cache_default_ttl: int = 300
    rate_limit_per_minute: int = 60
    rate_limit_login_per_minute: int = 5
    
    # --- MISCELLANEOUS CONFIGURATION ---
    prometheus_enabled: bool = True
    environment: str = "development"
    
    # --- FILE UPLOAD CONFIGURATION ---
    upload_directory: str = "./uploaded_files"
    max_file_size_mb: int = 50
    supported_file_types: str = ".pdf,.docx,.txt,.csv,.md"
    ocr_enabled: bool = True
    
    # --- RAG CONFIGURATION ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # --- EMBEDDING CONFIGURATION ---
    embedding_api_key: str = ""
    embedding_base_url: str = "https://openrouter.ai/api/v1"
    embedding_model: str = ""
    vector_dimension: int = 768
    pgvector_enabled: bool = True

    # --- PHASE 6: VECTOR SEARCH & RETRIEVAL CONFIGURATION ---
    default_top_k: int = 5
    default_similarity_threshold: float = 0.05
    vector_distance_metric: str = "cosine"  # cosine, l2, inner_product
    search_strategy: str = "vector"          # vector, hybrid_prepared
    hybrid_search_enabled: bool = False
    search_cache_enabled: bool = True
    search_cache_ttl: int = 300

    # --- PHASE 7: COMPLETE RAG PIPELINE CONFIGURATION ---
    rag_enabled: bool = True
    max_context_tokens: int = 3000
    max_context_chunks: int = 5
    enable_reranking: bool = True
    reranking_strategy: str = "lightweight"  # lightweight, cross_encoder_prepared
    grounding_strictness: str = "strict"      # strict, flexible
    enable_source_tracking: bool = True
    prompt_cache_ttl: int = 600
    prompt_template: str = "default_grounded"

    # --- PHASE 8: ADVANCED RAG PIPELINE CONFIGURATION ---
    enable_query_expansion: bool = True
    enable_hyde: bool = True
    enable_multi_query: bool = True
    enable_parent_child: bool = True
    enable_context_compression: bool = True
    enable_citations: bool = True
    enable_source_attribution: bool = True

    max_multi_queries: int = 3
    hyde_max_tokens: int = 250
    compression_ratio: float = 0.7  # Target context compression ratio (0.0 to 1.0)
    advanced_rag_cache_ttl: int = 300



    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    @model_validator(mode='after')
    def validate_embedding_config(self) -> 'Settings':
        if not self.embedding_model or not self.embedding_model.strip():
            raise ValueError(
                "EMBEDDING_MODEL is missing in .env. "
                "Please set it to a valid model (e.g., 'nomic-ai/nomic-embed-text-v1.5')."
            )
        if not self.embedding_api_key:
            logger.warning("[SETTINGS] EMBEDDING_API_KEY is empty. Embedding generation will fail.")
        return self


# lru_cache ensures we only load the .env file once, improving performance
@lru_cache()
def get_settings() -> Settings:
    logger.info("[SETTINGS] Loading configuration from .env file...")
    settings = Settings()

    # Mask API key for security — show only last 6 characters
    key = settings.openrouter_api_key
    masked = f"***{key[-6:]}" if len(key) > 6 else "***"

    logger.info(f"[SETTINGS] Configuration loaded successfully:")
    logger.info(f"  → API Key          : {masked}")
    logger.info(f"  → Model            : {settings.model_name}")
    logger.info(f"  → Base URL         : {settings.base_url}")
    logger.info(f"  → Temperature      : {settings.temperature}")
    logger.info(f"  → Max Tokens       : {settings.max_tokens}")
    logger.info(f"  → Top P            : {settings.top_p}")
    logger.info(f"  → Frequency Penalty: {settings.frequency_penalty}")
    logger.info(f"  → Embedding Model  : {settings.embedding_model}")
    logger.info(f"  → Vector Dimension : {settings.vector_dimension}")
    return settings
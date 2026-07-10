from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
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


# lru_cache ensures we only load the .env file once, improving performance
@lru_cache()
def get_settings() -> Settings:
    logger.info("[SETTINGS] Loading configuration from .env file...")
    settings = Settings()

    # Mask API key for security — show only last 6 characters
    key = settings.openrouter_api_key
    masked = f"***{key[-6:]}" if len(key) > 6 else "***"

    logger.info(f"[SETTINGS] ✅ Configuration loaded successfully:")
    logger.info(f"  → API Key          : {masked}")
    logger.info(f"  → Model            : {settings.model_name}")
    logger.info(f"  → Base URL         : {settings.base_url}")
    logger.info(f"  → Temperature      : {settings.temperature}")
    logger.info(f"  → Max Tokens       : {settings.max_tokens}")
    logger.info(f"  → Top P            : {settings.top_p}")
    logger.info(f"  → Frequency Penalty: {settings.frequency_penalty}")
    return settings
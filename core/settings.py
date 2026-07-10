from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

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
    return Settings()
# redis_client/client.py
import redis
import logging
from core.settings import get_settings
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisClientManager:
    """
    Manages the Redis connection pool with graceful degradation.
    If Redis is unavailable, the app will not crash; it will log a warning
    and return None, allowing the app to function without caching/rate-limiting.
    """
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._is_available = False

    def initialize(self):
        """Initialize the connection pool on startup."""
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=20,
                health_check_interval=30
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test the connection
            self._client.ping()
            self._is_available = True
            logger.info("[REDIS] ✅ Connection pool established successfully.")
        except redis.ConnectionError as e:
            self._is_available = False
            logger.warning(f"[REDIS] ⚠️ Connection failed: {e}. App will run without caching/rate-limiting.")
        except Exception as e:
            self._is_available = False
            logger.error(f"[REDIS] ❌ Unexpected error during initialization: {e}")

    @property
    def client(self) -> Optional[redis.Redis]:
        """Returns the Redis client if available, otherwise None."""
        if self._is_available and self._client:
            try:
                self._client.ping()
                return self._client
            except redis.ConnectionError:
                self._is_available = False
                logger.warning("[REDIS] ⚠️ Connection lost during runtime.")
                return None
        return None

    @property
    def is_available(self) -> bool:
        return self._is_available

# Global instance (Singleton pattern for connection pool)
redis_manager = RedisClientManager()

def get_redis_client() -> Optional[redis.Redis]:
    """
    FastAPI Dependency: Provides the Redis client.
    Returns None if Redis is down, enabling graceful degradation.
    """
    return redis_manager.client
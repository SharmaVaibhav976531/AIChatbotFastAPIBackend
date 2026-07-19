# services/cache_service.py
import json
import logging
from typing import Any, Optional
import redis
from monitoring.metrics import CACHE_HIT_TOTAL, CACHE_MISS_TOTAL

logger = logging.getLogger(__name__)

class CacheService:
    """
    Abstraction layer for Redis caching.
    Implements the Cache-Aside pattern with graceful degradation.
    If Redis is unavailable, all operations safely no-op, and the app 
    falls back to direct database queries.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis]):
        self.redis = redis_client

    def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            CACHE_MISS_TOTAL.inc()
            return None
        
        try:
            val = self.redis.get(key)
            from utils.educational_logger import EducationalLogger
            if val:
                logger.debug(f"[CACHE] HIT: {key}")
                EducationalLogger.log_cache_event(key, "HIT")
                CACHE_HIT_TOTAL.inc()
                return json.loads(val)
            
            logger.debug(f"[CACHE] MISS: {key}")
            EducationalLogger.log_cache_event(key, "MISS")
            CACHE_MISS_TOTAL.inc()
            return None
        except Exception as e:
            logger.warning(f"[CACHE] Error reading {key}: {e}")
            CACHE_MISS_TOTAL.inc()
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Store a value in the cache with a Time-To-Live (TTL) in seconds.
        """
        if not self.redis:
            return
        
        try:
            # default=str ensures datetime objects are serialized correctly
            serialized = json.dumps(value, default=str)
            self.redis.set(key, serialized, ex=ttl)
            logger.debug(f"[CACHE] SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"[CACHE] Error setting {key}: {e}")

    def delete(self, key: str):
        """Delete a specific key from the cache."""
        if not self.redis:
            return
        
        try:
            self.redis.delete(key)
            logger.debug(f"[CACHE] DELETE: {key}")
        except Exception as e:
            logger.warning(f"[CACHE] Error deleting {key}: {e}")

    def invalidate_user_cache(self, user_id: str):
        """
        Clear all cache entries for a specific user.
        Uses SCAN instead of KEYS to avoid blocking Redis in production.
        """
        if not self.redis:
            return
        
        try:
            pattern = f"user:{user_id}:*"
            # scan_iter is safe for production; KEYS is not.
            keys = list(self.redis.scan_iter(match=pattern, count=100))
            if keys:
                self.redis.delete(*keys)
                logger.info(f"[CACHE] Invalidated {len(keys)} keys for user {user_id}")
        except Exception as e:
            logger.warning(f"[CACHE] Error invalidating cache for user {user_id}: {e}")



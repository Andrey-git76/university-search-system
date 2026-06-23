import redis
import json
import hashlib
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for search results."""
    
    def __init__(self):
        try:
            self.redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.ttl = 300  # 5 minutes
            # Check connection
            self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.redis = None
            self.ttl = 300
    
    def _get_cache_key(self, query: str, limit: int, offset: int) -> str:
        """Generate a unique cache key."""
        data = f"{query}:{limit}:{offset}"
        return f"search:{hashlib.md5(data.encode()).hexdigest()}"
    
    def get(self, query: str, limit: int, offset: int):
        """Get cached results."""
        if not self.redis:
            return None
        try:
            key = self._get_cache_key(query, limit, offset)
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, query: str, limit: int, offset: int, results):
        """Save results to cache."""
        if not self.redis:
            return
        try:
            key = self._get_cache_key(query, limit, offset)
            self.redis.setex(key, self.ttl, json.dumps(results, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self, query: str = None):
        """Clear cache (all or by query)."""
        if not self.redis:
            return
        try:
            if query:
                # Delete keys containing this query
                pattern = f"search:*{hashlib.md5(query.encode()).hexdigest()}*"
                for key in self.redis.scan_iter(pattern):
                    self.redis.delete(key)
            else:
                self.redis.flushdb()
            logger.info(f"Cache cleared (query: {query})")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
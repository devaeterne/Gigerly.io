# api/app/core/redis.py
import redis.asyncio as redis
import logging
from typing import Optional, Any
import json
import pickle

from app.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection and utility manager"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
            
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return default
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis"""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment key value"""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    # Rate limiting helpers
    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Check rate limit for a key
        Returns (is_allowed, remaining_requests)
        """
        try:
            current = await self.redis.get(key)
            if current is None:
                await self.redis.setex(key, window, 1)
                return True, limit - 1
            
            current = int(current)
            if current >= limit:
                ttl = await self.redis.ttl(key)
                return False, 0
            
            await self.redis.incr(key)
            return True, limit - current - 1
            
        except Exception as e:
            logger.error(f"Rate limit check error for key {key}: {e}")
            return True, limit  # Allow on error
    
    # Cache helpers
    async def cache_set(self, key: str, value: Any, expire: int = 3600):
        """Set cache value with default 1 hour expiration"""
        cache_key = f"cache:{key}"
        return await self.set(cache_key, value, expire)
    
    async def cache_get(self, key: str, default: Any = None):
        """Get cache value"""
        cache_key = f"cache:{key}"
        return await self.get(cache_key, default)
    
    async def cache_delete(self, key: str):
        """Delete cache value"""
        cache_key = f"cache:{key}"
        return await self.delete(cache_key)
    
    async def health_check(self) -> bool:
        """Redis health check"""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

# Global Redis instance
redis_manager = RedisManager()

async def get_redis() -> RedisManager:
    """Dependency to get Redis manager"""
    return redis_manager
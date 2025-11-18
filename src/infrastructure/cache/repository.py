"""Cache repository - Multi-layer caching."""
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import hashlib

from cachetools import TTLCache
import redis.asyncio as aioredis

from config.settings import get_settings


class CacheRepository(ABC):
    """Cache repository interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass


class MultiLayerCacheRepository(CacheRepository):
    """Multi-layer cache - L1: Memory, L2: Redis."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # L1: In-memory cache
        self.memory_cache = TTLCache(maxsize=1000, ttl=60)
        
        # L2: Redis cache
        self.redis_client: Optional[aioredis.Redis] = None
        self._redis_connected = False
    
    async def _ensure_redis(self) -> None:
        """Ensure Redis connection."""
        if not self._redis_connected:
            try:
                self.redis_client = aioredis.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50
                )
                await self.redis_client.ping()
                self._redis_connected = True
            except Exception:
                # Redis not available, continue without it
                self._redis_connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (check L1, then L2)."""
        # Check L1: Memory
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check L2: Redis
        await self._ensure_redis()
        if self.redis_client and self._redis_connected:
            try:
                value = await self.redis_client.get(key)
                if value:
                    parsed = json.loads(value)
                    # Promote to L1
                    self.memory_cache[key] = parsed
                    return parsed
            except Exception:
                pass
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        """Set value in cache (both L1 and L2)."""
        # Set in L1
        self.memory_cache[key] = value
        
        # Set in L2
        await self._ensure_redis()
        if self.redis_client and self._redis_connected:
            try:
                serialized = json.dumps(value, default=str)
                await self.redis_client.setex(key, ttl, serialized)
            except Exception:
                pass
    
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        # Delete from L1
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Delete from L2
        await self._ensure_redis()
        if self.redis_client and self._redis_connected:
            try:
                await self.redis_client.delete(key)
            except Exception:
                pass
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate consistent cache key."""
        key_parts = []
        for arg in args:
            key_parts.append(str(arg))
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


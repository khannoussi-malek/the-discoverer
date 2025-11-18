"""Query result caching utilities."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json


@dataclass
class CachedResult:
    """Cached query result entity."""
    cache_key: str
    query: str
    database_ids: List[str]
    result: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class QueryResultCache:
    """In-memory query result cache with TTL support."""
    
    def __init__(self, default_ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            default_ttl_seconds: Default time-to-live in seconds
            max_size: Maximum number of cached items
        """
        self._cache: Dict[str, CachedResult] = {}
        self.default_ttl = default_ttl_seconds
        self.max_size = max_size
    
    @staticmethod
    def _generate_key(query: str, database_ids: Optional[List[str]] = None) -> str:
        """Generate cache key from query and database IDs."""
        key_data = {
            "query": query,
            "database_ids": sorted(database_ids) if database_ids else []
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(
        self,
        query: str,
        database_ids: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        cache_key = self._generate_key(query, database_ids)
        
        if cache_key not in self._cache:
            return None
        
        cached = self._cache[cache_key]
        
        # Check expiration
        if cached.expires_at and cached.expires_at < datetime.utcnow():
            del self._cache[cache_key]
            return None
        
        # Update access stats
        cached.access_count += 1
        cached.last_accessed = datetime.utcnow()
        
        return cached.result
    
    def set(
        self,
        query: str,
        database_ids: Optional[List[str]],
        result: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Cache a query result."""
        cache_key = self._generate_key(query, database_ids)
        
        # Evict if at max size
        if len(self._cache) >= self.max_size and cache_key not in self._cache:
            self._evict_oldest()
        
        ttl = ttl_seconds or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        cached = CachedResult(
            cache_key=cache_key,
            query=query,
            database_ids=database_ids or [],
            result=result,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._cache[cache_key] = cached
        return cache_key
    
    def _evict_oldest(self):
        """Evict the least recently accessed item."""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[oldest_key]
    
    def invalidate(
        self,
        query: Optional[str] = None,
        database_ids: Optional[List[str]] = None
    ) -> int:
        """
        Invalidate cached results.
        
        Args:
            query: Specific query to invalidate (None = all)
            database_ids: Specific database IDs to invalidate (None = all)
        
        Returns:
            Number of items invalidated
        """
        if query is None and database_ids is None:
            # Invalidate all
            count = len(self._cache)
            self._cache.clear()
            return count
        
        # Invalidate specific items
        keys_to_remove = []
        
        for key, cached in self._cache.items():
            if query and cached.query != query:
                continue
            if database_ids and set(cached.database_ids) != set(database_ids):
                continue
            keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]
        
        return len(keys_to_remove)
    
    def clear_expired(self) -> int:
        """Clear expired cache entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, cached in self._cache.items()
            if cached.expires_at and cached.expires_at < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self.clear_expired()  # Clean up expired first
        
        total_size = len(self._cache)
        total_accesses = sum(c.access_count for c in self._cache.values())
        
        return {
            "total_items": total_size,
            "max_size": self.max_size,
            "total_accesses": total_accesses,
            "hit_rate": None,  # Would need to track hits/misses
            "oldest_item": min(
                (c.last_accessed for c in self._cache.values()),
                default=None
            ).isoformat() if self._cache else None,
            "newest_item": max(
                (c.last_accessed for c in self._cache.values()),
                default=None
            ).isoformat() if self._cache else None
        }
    
    def list_keys(self) -> List[str]:
        """List all cache keys."""
        return list(self._cache.keys())
    
    def get_cache_info(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific cached item."""
        if cache_key not in self._cache:
            return None
        
        cached = self._cache[cache_key]
        return {
            "cache_key": cached.cache_key,
            "query": cached.query,
            "database_ids": cached.database_ids,
            "created_at": cached.created_at.isoformat(),
            "expires_at": cached.expires_at.isoformat() if cached.expires_at else None,
            "access_count": cached.access_count,
            "last_accessed": cached.last_accessed.isoformat(),
            "metadata": cached.metadata,
            "is_expired": cached.expires_at and cached.expires_at < datetime.utcnow()
        }



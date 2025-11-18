"""Cache management API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, List

from src.utils.query_result_cache import QueryResultCache


router = APIRouter(prefix="/api/cache", tags=["cache"])


def get_cache() -> QueryResultCache:
    """Dependency injection for query result cache."""
    from src.api.main import app
    if not hasattr(app.state, 'query_result_cache'):
        from src.utils.query_result_cache import QueryResultCache
        app.state.query_result_cache = QueryResultCache(
            default_ttl_seconds=3600,
            max_size=1000
        )
    return app.state.query_result_cache


@router.get("/stats")
async def get_cache_stats(cache: QueryResultCache = Depends(get_cache)):
    """Get cache statistics."""
    try:
        stats = cache.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def list_cache_keys(cache: QueryResultCache = Depends(get_cache)):
    """List all cache keys."""
    try:
        keys = cache.list_keys()
        return {
            "keys": keys,
            "total": len(keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/{cache_key}")
async def get_cache_info(
    cache_key: str,
    cache: QueryResultCache = Depends(get_cache)
):
    """Get information about a specific cached item."""
    try:
        info = cache.get_cache_info(cache_key)
        if not info:
            raise HTTPException(status_code=404, detail="Cache key not found")
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate")
async def invalidate_cache(
    query: Optional[str] = Body(None),
    database_ids: Optional[List[str]] = Body(None),
    cache: QueryResultCache = Depends(get_cache)
):
    """Invalidate cached results."""
    try:
        count = cache.invalidate(query=query, database_ids=database_ids)
        return {
            "message": f"Invalidated {count} cache entry(ies)",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_cache(cache: QueryResultCache = Depends(get_cache)):
    """Clear all cached results."""
    try:
        count = cache.invalidate()
        return {
            "message": f"Cleared {count} cache entry(ies)",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-expired")
async def clear_expired(cache: QueryResultCache = Depends(get_cache)):
    """Clear expired cache entries."""
    try:
        count = cache.clear_expired()
        return {
            "message": f"Cleared {count} expired cache entry(ies)",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



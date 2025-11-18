"""Analytics API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta

from src.utils.analytics import analytics_collector


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/stats")
async def get_usage_stats(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze")
):
    """Get usage statistics."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        stats = analytics_collector.get_stats(start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "stats": {
                "total_queries": stats.total_queries,
                "successful_queries": stats.successful_queries,
                "failed_queries": stats.failed_queries,
                "success_rate": stats.successful_queries / stats.total_queries if stats.total_queries > 0 else 0.0,
                "avg_execution_time": stats.avg_execution_time,
                "total_execution_time": stats.total_execution_time,
                "cache_hits": stats.cache_hits,
                "cache_misses": stats.cache_misses,
                "cache_hit_rate": stats.cache_hits / stats.total_queries if stats.total_queries > 0 else 0.0,
                "database_usage": stats.database_usage,
                "query_types": stats.query_types
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-queries")
async def get_top_queries(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=365)
):
    """Get most frequently executed queries."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        top_queries = analytics_collector.get_top_queries(limit, start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "top_queries": top_queries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/{database_id}")
async def get_database_analytics(
    database_id: str,
    days: int = Query(7, ge=1, le=365)
):
    """Get analytics for a specific database."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        stats = analytics_collector.get_database_stats(database_id, start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "database_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



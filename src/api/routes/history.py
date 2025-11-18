"""Query history API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from src.infrastructure.query_history.repository import QueryHistoryRepository


router = APIRouter(prefix="/api/history", tags=["history"])


def get_history_repository() -> QueryHistoryRepository:
    """Dependency injection for history repository."""
    from src.api.main import app
    return app.state.query_history_repository


@router.get("/queries")
async def get_query_history(
    limit: int = Query(10, ge=1, le=100),
    database_id: Optional[str] = None,
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Get recent query history."""
    try:
        history = await repository.get_recent(limit=limit, database_id=database_id)
        return {
            "queries": [
                {
                    "query_id": entry["query"].id,
                    "user_query": entry["query"].user_query,
                    "generated_query": entry["query"].generated_query,
                    "query_type": entry["query"].query_type,
                    "database_id": entry["query"].database_id,
                    "timestamp": entry["timestamp"].isoformat(),
                    "execution_time": (
                        entry["result"].execution_time
                        if entry.get("result") else None
                    )
                }
                for entry in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/{query_id}")
async def get_query_by_id(
    query_id: str,
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Get query by ID."""
    entry = await repository.get_by_id(query_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return {
        "query_id": entry["query"].id,
        "user_query": entry["query"].user_query,
        "generated_query": entry["query"].generated_query,
        "query_type": entry["query"].query_type,
        "database_id": entry["query"].database_id,
        "timestamp": entry["timestamp"].isoformat(),
        "result": {
            "total_rows": entry["result"].total_rows if entry.get("result") else None,
            "execution_time": entry["result"].execution_time if entry.get("result") else None
        }
    }


@router.get("/queries/search")
async def search_query_history(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Search query history."""
    try:
        results = await repository.search(q, limit=limit)
        return {
            "queries": [
                {
                    "query_id": entry["query"].id,
                    "user_query": entry["query"].user_query,
                    "timestamp": entry["timestamp"].isoformat()
                }
                for entry in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_query_statistics(
    days: int = Query(7, ge=1, le=30),
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Get query statistics."""
    try:
        stats = await repository.get_statistics(days=days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


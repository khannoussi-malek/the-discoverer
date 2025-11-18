"""Batch query API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from src.application.services.batch_query_service import BatchQueryService, BatchQueryRequest
from src.api.models.response import QueryResponse


router = APIRouter(prefix="/api/batch", tags=["batch"])


class BatchQueryItem(BaseModel):
    """Single query in batch."""
    query: str
    database_ids: Optional[List[str]] = None
    priority: int = 0


class BatchQueryRequestModel(BaseModel):
    """Batch query request."""
    queries: List[BatchQueryItem]
    max_concurrent: int = 5
    stop_on_error: bool = False
    sequential: bool = False


def get_batch_service() -> BatchQueryService:
    """Dependency injection for batch service."""
    from src.api.main import app
    return app.state.batch_service


@router.post("/execute")
async def execute_batch(
    request: BatchQueryRequestModel,
    service: BatchQueryService = Depends(get_batch_service)
):
    """Execute multiple queries in batch."""
    try:
        # Convert to batch requests
        batch_requests = [
            BatchQueryRequest(
                query=item.query,
                database_ids=item.database_ids,
                priority=item.priority
            )
            for item in request.queries
        ]
        
        # Execute
        if request.sequential:
            results = await service.execute_sequential(
                batch_requests,
                stop_on_error=request.stop_on_error
            )
        else:
            results = await service.execute_batch(
                batch_requests,
                max_concurrent=request.max_concurrent,
                stop_on_error=request.stop_on_error
            )
        
        # Format response
        response_data = []
        for result in results:
            if result.success and result.result:
                query_id = list(result.result.results.values())[0].query_id if result.result.results else ""
                response_data.append({
                    "query": result.request.query,
                    "success": True,
                    "query_id": query_id,
                    "total_rows": result.result.total_rows,
                    "execution_time": result.execution_time,
                    "databases_queried": result.result.databases_queried
                })
            else:
                response_data.append({
                    "query": result.request.query,
                    "success": False,
                    "error": result.error,
                    "execution_time": result.execution_time
                })
        
        return {
            "total": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



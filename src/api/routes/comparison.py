"""Query result comparison API routes."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from src.application.services.query_comparison_service import QueryComparisonService


router = APIRouter(prefix="/api/comparison", tags=["comparison"])


def get_comparison_service() -> QueryComparisonService:
    """Dependency injection for comparison service."""
    return QueryComparisonService()


@router.get("/compare")
async def compare_queries(
    query1_id: str = Query(..., description="First query ID"),
    query2_id: str = Query(..., description="Second query ID"),
    service: QueryComparisonService = Depends(get_comparison_service)
):
    """Compare two query results."""
    try:
        comparison = await service.compare_by_query_ids(query1_id, query2_id)
        
        return {
            "query1_id": comparison.query1_id,
            "query2_id": comparison.query2_id,
            "compared_at": comparison.compared_at.isoformat(),
            "similarity_score": comparison.similarity_score,
            "row_count_diff": comparison.row_count_diff,
            "differences": comparison.differences,
            "column_differences": comparison.column_differences,
            "value_differences": comparison.value_differences[:100]  # Limit to first 100
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

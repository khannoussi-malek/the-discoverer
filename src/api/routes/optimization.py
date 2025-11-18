"""Query optimization API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.api.models.request import QueryRequest
from src.utils.query_optimizer import QueryOptimizer


router = APIRouter(prefix="/api/optimization", tags=["optimization"])


@router.post("/analyze")
async def analyze_query_optimization(
    request: QueryRequest
):
    """Analyze query for optimization opportunities."""
    try:
        analysis = QueryOptimizer.analyze_sql(request.query)
        suggestions = QueryOptimizer.suggest_indexes(request.query)
        complexity = QueryOptimizer.estimate_complexity(request.query)
        
        return {
            "query": request.query,
            "optimization": analysis,
            "index_suggestions": suggestions,
            "complexity": complexity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-indexes")
async def suggest_indexes(
    request: QueryRequest,
    schema: Optional[dict] = None
):
    """Suggest indexes for a query."""
    try:
        suggestions = QueryOptimizer.suggest_indexes(request.query, schema)
        return {
            "query": request.query,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complexity")
async def estimate_complexity(
    request: QueryRequest
):
    """Estimate query complexity."""
    try:
        complexity = QueryOptimizer.estimate_complexity(request.query)
        return {
            "query": request.query,
            "complexity": complexity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



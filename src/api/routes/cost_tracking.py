"""Cost tracking API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta

from src.utils.cost_tracker import CostTracker


router = APIRouter(prefix="/api/cost-tracking", tags=["cost-tracking"])


def get_cost_tracker() -> CostTracker:
    """Dependency injection for cost tracker."""
    from src.api.main import app
    if not hasattr(app.state, 'cost_tracker'):
        from src.utils.cost_tracker import CostTracker
        app.state.cost_tracker = CostTracker()
    return app.state.cost_tracker


@router.get("/stats")
async def get_cost_stats(
    days: int = Query(7, description="Number of days to analyze"),
    model: Optional[str] = Query(None, description="Filter by model"),
    operation: Optional[str] = Query(None, description="Filter by operation"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    tracker: CostTracker = Depends(get_cost_tracker)
):
    """Get cost and usage statistics."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        stats = tracker.get_usage_stats(
            start_date=start_date,
            model=model,
            operation=operation,
            user_id=user_id
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/total")
async def get_total_cost(
    days: int = Query(7, description="Number of days to analyze"),
    model: Optional[str] = Query(None, description="Filter by model"),
    operation: Optional[str] = Query(None, description="Filter by operation"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    tracker: CostTracker = Depends(get_cost_tracker)
):
    """Get total cost."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        total_cost = tracker.get_total_cost(
            start_date=start_date,
            model=model,
            operation=operation,
            user_id=user_id
        )
        return {
            "total_cost_usd": total_cost,
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-model")
async def get_cost_by_model(
    days: int = Query(7, description="Number of days to analyze"),
    tracker: CostTracker = Depends(get_cost_tracker)
):
    """Get cost breakdown by model."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        costs = tracker.get_cost_by_model(start_date=start_date)
        return {
            "costs_by_model": costs,
            "total": sum(costs.values()),
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-operation")
async def get_cost_by_operation(
    days: int = Query(7, description="Number of days to analyze"),
    tracker: CostTracker = Depends(get_cost_tracker)
):
    """Get cost breakdown by operation."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        costs = tracker.get_cost_by_operation(start_date=start_date)
        return {
            "costs_by_operation": costs,
            "total": sum(costs.values()),
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily")
async def get_daily_costs(
    days: int = Query(7, description="Number of days to analyze"),
    tracker: CostTracker = Depends(get_cost_tracker)
):
    """Get daily cost breakdown."""
    try:
        daily_costs = tracker.get_daily_costs(days=days)
        return {
            "daily_costs": daily_costs,
            "total_cost": sum(d["cost_usd"] for d in daily_costs),
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



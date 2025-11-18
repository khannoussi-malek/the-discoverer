"""Statistics and monitoring API routes."""
from fastapi import APIRouter, Depends

from src.utils.performance import performance_monitor


router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics."""
    stats = performance_monitor.get_stats()
    return {
        "metrics": stats,
        "summary": {
            "total_operations": sum(
                metric["count"] for metric in stats.values()
            ),
            "operations_tracked": len(stats)
        }
    }


@router.post("/performance/reset")
async def reset_performance_stats():
    """Reset performance statistics."""
    performance_monitor.reset()
    return {"status": "success", "message": "Performance stats reset"}


"""Health check API routes."""
from fastapi import APIRouter, Depends
from typing import Dict
from datetime import datetime

from src.infrastructure.database.health_monitor import DatabaseHealthMonitor


router = APIRouter(prefix="/api/health", tags=["health"])


def get_health_monitor() -> DatabaseHealthMonitor:
    """Dependency injection for health monitor."""
    from src.api.main import app
    return app.state.health_monitor


@router.get("/databases")
async def get_database_health(
    health_monitor: DatabaseHealthMonitor = Depends(get_health_monitor)
):
    """Get health status of all databases."""
    statuses = health_monitor.get_all_status()
    return {
        "databases": statuses,
        "total": len(statuses),
        "healthy": sum(
            1 for s in statuses.values()
            if s.get("status") == "healthy"
        ),
        "unhealthy": sum(
            1 for s in statuses.values()
            if s.get("status") == "unhealthy"
        )
    }


@router.get("/databases/{db_id}")
async def get_database_health_by_id(
    db_id: str,
    health_monitor: DatabaseHealthMonitor = Depends(get_health_monitor)
):
    """Get health status of a specific database."""
    # Check immediately
    status = await health_monitor.check_health(db_id)
    return status


@router.post("/databases/check-all")
async def check_all_databases(
    health_monitor: DatabaseHealthMonitor = Depends(get_health_monitor)
):
    """Manually trigger health check for all databases."""
    results = await health_monitor.check_all()
    return {
        "results": results,
        "checked_at": datetime.now().isoformat()
    }


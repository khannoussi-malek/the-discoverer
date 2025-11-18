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
    statuses = health_monitor.get_all_health()
    # Convert DatabaseHealth objects to dicts
    statuses_dict = {
        db_id: {
            "database_id": health.database_id,
            "status": "healthy" if health.is_healthy else "unhealthy",
            "last_check": health.last_check.isoformat() if health.last_check else None,
            "last_success": health.last_success.isoformat() if health.last_success else None,
            "consecutive_failures": health.consecutive_failures,
            "response_time": health.response_time,
            "error_message": health.error_message
        }
        for db_id, health in statuses.items()
    }
    return {
        "databases": statuses_dict,
        "total": len(statuses_dict),
        "healthy": sum(
            1 for s in statuses_dict.values()
            if s.get("status") == "healthy"
        ),
        "unhealthy": sum(
            1 for s in statuses_dict.values()
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
    health = await health_monitor.check_database(db_id)
    # Convert DatabaseHealth to dict
    return {
        "database_id": health.database_id,
        "status": "healthy" if health.is_healthy else "unhealthy",
        "last_check": health.last_check.isoformat() if health.last_check else None,
        "last_success": health.last_success.isoformat() if health.last_success else None,
        "consecutive_failures": health.consecutive_failures,
        "response_time": health.response_time,
        "error_message": health.error_message
    }


@router.post("/databases/check-all")
async def check_all_databases(
    health_monitor: DatabaseHealthMonitor = Depends(get_health_monitor)
):
    """Manually trigger health check for all databases."""
    await health_monitor.check_all_databases()
    # Get updated health status
    statuses = health_monitor.get_all_health()
    # Convert DatabaseHealth objects to dicts
    results = {
        db_id: {
            "database_id": health.database_id,
            "status": "healthy" if health.is_healthy else "unhealthy",
            "last_check": health.last_check.isoformat() if health.last_check else None,
            "last_success": health.last_success.isoformat() if health.last_success else None,
            "consecutive_failures": health.consecutive_failures,
            "response_time": health.response_time,
            "error_message": health.error_message
        }
        for db_id, health in statuses.items()
    }
    return {
        "results": results,
        "checked_at": datetime.now().isoformat()
    }


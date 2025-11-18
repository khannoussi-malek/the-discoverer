"""Connection pool management API routes."""
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Optional, Dict, Any

from src.infrastructure.database.pool_manager import (
    ConnectionPoolManager,
    PoolConfig,
    PoolStatus
)
from src.infrastructure.database.repository import DatabaseRepository


router = APIRouter(prefix="/api/pools", tags=["connection-pools"])


def get_pool_manager() -> ConnectionPoolManager:
    """Dependency injection for pool manager."""
    from src.api.main import app
    if not hasattr(app.state, 'pool_manager'):
        from src.infrastructure.database.pool_manager import ConnectionPoolManager
        app.state.pool_manager = ConnectionPoolManager()
    return app.state.pool_manager


def get_database_repository() -> DatabaseRepository:
    """Dependency injection for database repository."""
    from src.api.main import app
    return app.state.database_repository


@router.get("")
async def list_pools(
    manager: ConnectionPoolManager = Depends(get_pool_manager)
):
    """List all connection pools."""
    try:
        stats = manager.get_all_pool_stats()
        return {
            "pools": [
                {
                    "database_id": db_id,
                    "status": stat.status.value,
                    "min_size": stat.min_size,
                    "max_size": stat.max_size,
                    "current_size": stat.current_size,
                    "active_connections": stat.active_connections,
                    "idle_connections": stat.idle_connections,
                    "total_queries": stat.total_queries,
                    "failed_queries": stat.failed_queries,
                    "last_used": stat.last_used.isoformat() if stat.last_used else None,
                    "uptime_seconds": stat.uptime_seconds
                }
                for db_id, stat in stats.items()
            ],
            "total": len(stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{database_id}")
async def get_pool(
    database_id: str,
    manager: ConnectionPoolManager = Depends(get_pool_manager)
):
    """Get pool information for a database."""
    try:
        stats = manager.get_pool_stats(database_id)
        config = manager.get_pool_config(database_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        return {
            "database_id": database_id,
            "status": stats.status.value,
            "config": {
                "min_size": config.min_size if config else None,
                "max_size": config.max_size if config else None,
                "max_queries": config.max_queries if config else None,
                "max_inactive_time": config.max_inactive_time if config else None,
                "timeout": config.timeout if config else None
            },
            "stats": {
                "current_size": stats.current_size,
                "active_connections": stats.active_connections,
                "idle_connections": stats.idle_connections,
                "total_queries": stats.total_queries,
                "failed_queries": stats.failed_queries,
                "created_at": stats.created_at.isoformat(),
                "last_used": stats.last_used.isoformat() if stats.last_used else None,
                "uptime_seconds": stats.uptime_seconds
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{database_id}/health")
async def pool_health_check(
    database_id: str,
    manager: ConnectionPoolManager = Depends(get_pool_manager)
):
    """Perform health check on pool."""
    try:
        health = await manager.health_check(database_id)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{database_id}/config")
async def update_pool_config(
    database_id: str,
    config: Dict[str, Any] = Body(...),
    manager: ConnectionPoolManager = Depends(get_pool_manager),
    db_repo: DatabaseRepository = Depends(get_database_repository)
):
    """Update pool configuration."""
    try:
        # Get database
        database = await db_repo.get_by_id(database_id)
        if not database:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Create pool config
        pool_config = PoolConfig(
            min_size=config.get("min_size", 2),
            max_size=config.get("max_size", 10),
            max_queries=config.get("max_queries", 50000),
            max_inactive_time=config.get("max_inactive_time", 300.0),
            timeout=config.get("timeout", 30.0)
        )
        
        success = await manager.update_pool_config(database_id, pool_config)
        if not success:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        return {
            "message": "Pool configuration updated",
            "config": {
                "min_size": pool_config.min_size,
                "max_size": pool_config.max_size,
                "max_queries": pool_config.max_queries,
                "max_inactive_time": pool_config.max_inactive_time,
                "timeout": pool_config.timeout
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{database_id}/refresh")
async def refresh_pool(
    database_id: str,
    manager: ConnectionPoolManager = Depends(get_pool_manager)
):
    """Refresh connection pool (close and recreate)."""
    try:
        success = await manager.refresh_pool(database_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        return {"message": "Pool refreshed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{database_id}")
async def close_pool(
    database_id: str,
    manager: ConnectionPoolManager = Depends(get_pool_manager)
):
    """Close connection pool."""
    try:
        success = await manager.close_pool(database_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        return {"message": "Pool closed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{database_id}/initialize")
async def initialize_pool(
    database_id: str,
    config: Optional[Dict[str, Any]] = Body(None),
    manager: ConnectionPoolManager = Depends(get_pool_manager),
    db_repo: DatabaseRepository = Depends(get_database_repository)
):
    """Initialize connection pool for a database."""
    try:
        # Get database
        database = await db_repo.get_by_id(database_id)
        if not database:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Create pool config if provided
        pool_config = None
        if config:
            pool_config = PoolConfig(
                min_size=config.get("min_size", 2),
                max_size=config.get("max_size", 10),
                max_queries=config.get("max_queries", 50000),
                max_inactive_time=config.get("max_inactive_time", 300.0),
                timeout=config.get("timeout", 30.0)
            )
        
        # Get or create pool
        adapter = await manager.get_pool(database, pool_config)
        
        return {
            "message": "Pool initialized successfully",
            "database_id": database_id,
            "connected": adapter.is_connected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




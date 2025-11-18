"""Discovery API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.api.models.request import DatabaseConfigRequest
from src.api.models.response import DatabaseResponse, ErrorResponse
from src.application.services.discovery_service import DiscoveryService


router = APIRouter(prefix="/api/discovery", tags=["discovery"])


def get_discovery_service() -> DiscoveryService:
    """Dependency injection for discovery service."""
    # This will be injected from app state
    from src.api.main import app
    return app.state.discovery_service


@router.post("/databases", response_model=DatabaseResponse)
async def register_database(
    config: DatabaseConfigRequest,
    service: DiscoveryService = Depends(get_discovery_service)
):
    """Register and discover a new database."""
    try:
        database = await service.discover_database(config.dict())
        return DatabaseResponse(
            id=database.id,
            type=database.type,
            name=database.name,
            host=database.host,
            port=database.port,
            database_name=database.database_name,
            is_active=database.is_active,
            last_synced=database.last_synced.isoformat() if database.last_synced else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/databases", response_model=List[DatabaseResponse])
async def list_databases(
    service: DiscoveryService = Depends(get_discovery_service)
):
    """List all registered databases."""
    from src.infrastructure.database.repository import InMemoryDatabaseRepository
    repository = InMemoryDatabaseRepository()
    databases = await repository.get_all()
    
    return [
        DatabaseResponse(
            id=db.id,
            type=db.type,
            name=db.name,
            host=db.host,
            port=db.port,
            database_name=db.database_name,
            is_active=db.is_active,
            last_synced=db.last_synced.isoformat() if db.last_synced else None
        )
        for db in databases
    ]


@router.post("/databases/{db_id}/sync", response_model=DatabaseResponse)
async def sync_database(
    db_id: str,
    service: DiscoveryService = Depends(get_discovery_service)
):
    """Sync database schema."""
    try:
        schema = await service.sync_schema(db_id)
        from src.infrastructure.database.repository import InMemoryDatabaseRepository
        repository = InMemoryDatabaseRepository()
        database = await repository.get_by_id(db_id)
        
        if not database:
            raise HTTPException(status_code=404, detail="Database not found")
        
        return DatabaseResponse(
            id=database.id,
            type=database.type,
            name=database.name,
            host=database.host,
            port=database.port,
            database_name=database.database_name,
            is_active=database.is_active,
            last_synced=database.last_synced.isoformat() if database.last_synced else None
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


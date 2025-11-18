"""Management API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient


router = APIRouter(prefix="/api/management", tags=["management"])


def get_db_repository() -> DatabaseRepository:
    """Dependency injection for database repository."""
    from src.api.main import app
    return app.state.db_repository


def get_vector_db_client() -> QdrantVectorDBClient:
    """Dependency injection for vector DB client."""
    from src.api.main import app
    return app.state.vector_db_client


@router.get("/databases/count")
async def get_database_count(
    repository: DatabaseRepository = Depends(get_db_repository)
):
    """Get total number of registered databases."""
    databases = await repository.get_all()
    return {
        "total": len(databases),
        "by_type": {
            db.type: sum(1 for d in databases if d.type == db.type)
            for db in databases
        }
    }


@router.get("/vector-db/info")
async def get_vector_db_info(
    vector_db: QdrantVectorDBClient = Depends(get_vector_db_client)
):
    """Get vector database information."""
    from config.settings import get_settings
    settings = get_settings()
    
    try:
        schemas_info = await vector_db.get_collection_info(
            settings.qdrant_collection_schemas
        )
        content_info = await vector_db.get_collection_info(
            settings.qdrant_collection_content
        )
        
        return {
            "schemas_collection": schemas_info,
            "content_collection": content_info,
            "url": settings.qdrant_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/databases/{db_id}")
async def delete_database(
    db_id: str,
    repository: DatabaseRepository = Depends(get_db_repository)
):
    """Delete a database registration."""
    database = await repository.get_by_id(db_id)
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    
    await repository.delete(db_id)
    return {"status": "success", "message": f"Database {db_id} deleted"}


@router.get("/system/info")
async def get_system_info():
    """Get system information."""
    from config.settings import get_settings
    import sys
    import platform
    
    settings = get_settings()
    
    return {
        "application": {
            "name": settings.app_name,
            "version": settings.app_version
        },
        "python": {
            "version": sys.version,
            "platform": platform.platform()
        },
        "configuration": {
            "vector_db_url": settings.qdrant_url,
            "redis_url": settings.redis_url,
            "embedding_model": settings.embedding_model,
            "llm_model": settings.openai_model
        }
    }


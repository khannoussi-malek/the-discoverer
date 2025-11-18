"""Query versioning API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.utils.query_versioning import QueryVersionManager


router = APIRouter(prefix="/api/versioning", tags=["versioning"])


def get_version_manager() -> QueryVersionManager:
    """Dependency injection for version manager."""
    from src.api.main import app
    if not hasattr(app.state, 'version_manager'):
        app.state.version_manager = QueryVersionManager()
    return app.state.version_manager


@router.get("/{query_id}/versions")
async def get_versions(
    query_id: str,
    manager: QueryVersionManager = Depends(get_version_manager)
):
    """Get all versions of a query."""
    try:
        versions = await manager.get_versions(query_id)
        return {
            "query_id": query_id,
            "total_versions": len(versions),
            "versions": [
                {
                    "id": v.id,
                    "version": v.version,
                    "query_text": v.query_text,
                    "generated_query": v.generated_query,
                    "result_hash": v.result_hash,
                    "created_at": v.created_at.isoformat(),
                    "created_by": v.created_by,
                    "notes": v.notes,
                    "is_current": v.is_current
                }
                for v in versions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{query_id}/current")
async def get_current_version(
    query_id: str,
    manager: QueryVersionManager = Depends(get_version_manager)
):
    """Get current version of a query."""
    try:
        version = await manager.get_current_version(query_id)
        if not version:
            raise HTTPException(status_code=404, detail="No versions found")
        
        return {
            "id": version.id,
            "version": version.version,
            "query_text": version.query_text,
            "generated_query": version.generated_query,
            "result_hash": version.result_hash,
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
            "notes": version.notes,
            "is_current": version.is_current
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{query_id}/versions/{version}")
async def get_version(
    query_id: str,
    version: int,
    manager: QueryVersionManager = Depends(get_version_manager)
):
    """Get specific version of a query."""
    try:
        v = await manager.get_version(query_id, version)
        if not v:
            raise HTTPException(status_code=404, detail="Version not found")
        
        return {
            "id": v.id,
            "version": v.version,
            "query_text": v.query_text,
            "generated_query": v.generated_query,
            "result_hash": v.result_hash,
            "created_at": v.created_at.isoformat(),
            "created_by": v.created_by,
            "notes": v.notes,
            "is_current": v.is_current
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{query_id}/versions/{version}/set-current")
async def set_current_version(
    query_id: str,
    version: int,
    manager: QueryVersionManager = Depends(get_version_manager)
):
    """Set a version as current."""
    try:
        success = await manager.set_current_version(query_id, version)
        if not success:
            raise HTTPException(status_code=404, detail="Version not found")
        
        return {"message": f"Version {version} set as current"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{query_id}/compare")
async def compare_versions(
    query_id: str,
    version1: int = Query(..., description="First version"),
    version2: int = Query(..., description="Second version"),
    manager: QueryVersionManager = Depends(get_version_manager)
):
    """Compare two versions of a query."""
    try:
        comparison = await manager.compare_versions(query_id, version1, version2)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



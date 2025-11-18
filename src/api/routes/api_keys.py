"""API key management routes."""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from datetime import datetime

from src.api.models.request import APIKeyCreateRequest, APIKeyUpdateRequest
from src.infrastructure.auth.api_key_manager import APIKeyManager
from src.infrastructure.auth.user_repository import User, UserRepository


router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


def get_api_key_manager() -> APIKeyManager:
    """Dependency injection for API key manager."""
    from src.api.main import app
    if not hasattr(app.state, 'api_key_manager'):
        app.state.api_key_manager = APIKeyManager()
    return app.state.api_key_manager


@router.post("")
async def create_api_key(
    request: APIKeyCreateRequest,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """Create a new API key."""
    try:
        key, api_key = await manager.create_key(
            name=request.name,
            user_id=None,  # Can be set based on authentication
            scopes=request.scopes,
            expires_in_days=request.expires_in_days,
            rate_limit=request.rate_limit,
            metadata=request.metadata or {}
        )
        
        return {
            "id": api_key.id,
            "key": key,  # Only returned once!
            "name": api_key.name,
            "scopes": api_key.scopes,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "created_at": api_key.created_at.isoformat(),
            "rate_limit": api_key.rate_limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_api_keys(
    active_only: bool = False,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """List API keys."""
    try:
        user_id = None  # Can filter by user_id if authenticated
        keys = await manager.list_keys(user_id=user_id, active_only=active_only)
        
        return {
            "keys": [
                {
                    "id": k.id,
                    "name": k.name,
                    "scopes": k.scopes,
                    "created_at": k.created_at.isoformat(),
                    "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                    "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                    "is_active": k.is_active,
                    "rate_limit": k.rate_limit
                }
                for k in keys
            ],
            "total": len(keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key_id}")
async def get_api_key(
    key_id: str,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """Get API key details."""
    try:
        api_key = await manager.get_key(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Ownership check can be added if authentication is implemented
        
        return {
            "id": api_key.id,
            "name": api_key.name,
            "scopes": api_key.scopes,
            "created_at": api_key.created_at.isoformat(),
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "is_active": api_key.is_active,
            "rate_limit": api_key.rate_limit,
            "metadata": api_key.metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{key_id}")
async def update_api_key(
    key_id: str,
    request: APIKeyUpdateRequest,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """Update API key."""
    try:
        api_key = await manager.get_key(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Ownership check can be added if authentication is implemented
        
        updated = await manager.update_key(
            key_id=key_id,
            name=request.name,
            scopes=request.scopes,
            is_active=request.is_active,
            rate_limit=request.rate_limit,
            metadata=request.metadata
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {
            "id": updated.id,
            "name": updated.name,
            "scopes": updated.scopes,
            "is_active": updated.is_active,
            "rate_limit": updated.rate_limit,
            "metadata": updated.metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """Revoke an API key."""
    try:
        api_key = await manager.get_key(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Ownership check can be added if authentication is implemented
        
        success = await manager.revoke_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"message": "API key revoked"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    manager: APIKeyManager = Depends(get_api_key_manager),
):
    """Delete an API key permanently."""
    try:
        api_key = await manager.get_key(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Ownership check can be added if authentication is implemented
        
        success = await manager.delete_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"message": "API key deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""Query result sharing API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, List

from src.application.services.query_result_sharing import QueryResultSharingService
from src.infrastructure.query_history.repository import QueryHistoryRepository


router = APIRouter(prefix="/api/sharing", tags=["sharing"])


def get_sharing_service() -> QueryResultSharingService:
    """Dependency injection for sharing service."""
    from src.api.main import app
    if not hasattr(app.state, 'sharing_service'):
        from src.utils.query_result_sharing import QueryResultSharingService
        app.state.sharing_service = QueryResultSharingService()
    return app.state.sharing_service


def get_history_repository() -> QueryHistoryRepository:
    """Dependency injection for history repository."""
    from src.api.main import app
    return app.state.query_history_repository


@router.post("")
async def create_share(
    query_id: str = Body(..., description="Query ID to share"),
    expires_in_hours: Optional[int] = Body(None, description="Hours until expiration"),
    max_accesses: Optional[int] = Body(None, description="Maximum number of accesses"),
    allowed_emails: Optional[List[str]] = Body(None, description="Allowed email addresses"),
    password: Optional[str] = Body(None, description="Password protection"),
    service: QueryResultSharingService = Depends(get_sharing_service)
):
    """Create a shareable link for a query result."""
    try:
        # Verify query exists
        history_repo = get_history_repository()
        query_history = await history_repo.get_by_id(query_id)
        if not query_history:
            raise HTTPException(status_code=404, detail="Query not found")
        
        shared_result = await service.create_share(
            query_id=query_id,
            expires_in_hours=expires_in_hours,
            max_accesses=max_accesses,
            allowed_emails=allowed_emails,
            password=password
        )
        
        share_url = service.get_share_url(shared_result.share_token)
        
        return {
            "share_id": shared_result.share_id,
            "share_token": shared_result.share_token,
            "share_url": share_url,
            "expires_at": shared_result.expires_at.isoformat() if shared_result.expires_at else None,
            "max_accesses": shared_result.max_accesses,
            "created_at": shared_result.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{share_token}")
async def get_shared_result(
    share_token: str,
    password: Optional[str] = Query(None, description="Password if protected"),
    service: QueryResultSharingService = Depends(get_sharing_service),
    history_repo: QueryHistoryRepository = Depends(get_history_repository)
):
    """Get shared query result by token."""
    try:
        shared_result = await service.get_share(share_token, password)
        if not shared_result:
            raise HTTPException(status_code=404, detail="Share not found or expired")
        
        # Get query result
        query_history = await history_repo.get_by_id(shared_result.query_id)
        if not query_history:
            raise HTTPException(status_code=404, detail="Query result not found")
        
        return {
            "query_id": shared_result.query_id,
            "share_id": shared_result.share_id,
            "result": query_history.result,
            "created_at": shared_result.created_at.isoformat(),
            "access_count": shared_result.access_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_shares(
    query_id: Optional[str] = Query(None),
    service: QueryResultSharingService = Depends(get_sharing_service)
):
    """List shared results."""
    try:
        shares = await service.list_shares(query_id=query_id)
        
        return {
            "shares": [
                {
                    "share_id": s.share_id,
                    "query_id": s.query_id,
                    "share_token": s.share_token,
                    "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                    "access_count": s.access_count,
                    "max_accesses": s.max_accesses,
                    "is_active": s.is_active,
                    "created_at": s.created_at.isoformat()
                }
                for s in shares
            ],
            "total": len(shares)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{share_id}/revoke")
async def revoke_share(
    share_id: str,
    service: QueryResultSharingService = Depends(get_sharing_service)
):
    """Revoke a shared result."""
    try:
        success = await service.revoke_share(share_id)
        if not success:
            raise HTTPException(status_code=404, detail="Share not found")
        
        return {"message": "Share revoked"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{share_id}")
async def delete_share(
    share_id: str,
    service: QueryResultSharingService = Depends(get_sharing_service)
):
    """Delete a shared result."""
    try:
        success = await service.delete_share(share_id)
        if not success:
            raise HTTPException(status_code=404, detail="Share not found")
        
        return {"message": "Share deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


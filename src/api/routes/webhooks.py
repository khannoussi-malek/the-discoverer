"""Webhook API routes."""
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Optional, Dict, Any

from datetime import datetime
from src.utils.webhooks import WebhookService, WebhookEvent
from src.api.models.request import WebhookCreateRequest, WebhookUpdateRequest


router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def get_webhook_service() -> WebhookService:
    """Dependency injection for webhook service."""
    from src.api.main import app
    if not hasattr(app.state, 'webhook_service'):
        from src.utils.webhooks import WebhookService
        app.state.webhook_service = WebhookService()
    return app.state.webhook_service


@router.post("")
async def create_webhook(
    request: WebhookCreateRequest,
    service: WebhookService = Depends(get_webhook_service)
):
    """Create a new webhook."""
    try:
        # Convert event strings to WebhookEvent enum
        events = [WebhookEvent(e) for e in request.events]
        
        webhook = service.create_webhook(
            url=request.url,
            events=events,
            headers=request.headers,
            timeout=request.timeout or 30
        )
        
        return {
            "id": webhook.id,
            "url": webhook.url,
            "events": [e.value for e in webhook.events],
            "secret": webhook.secret,  # Only returned on creation
            "active": webhook.active,
            "created_at": webhook.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_webhooks(
    event: Optional[str] = Query(None, description="Filter by event type"),
    active_only: bool = Query(False, description="Only return active webhooks"),
    service: WebhookService = Depends(get_webhook_service)
):
    """List webhooks."""
    try:
        webhook_event = WebhookEvent(event) if event else None
        webhooks = service.list_webhooks(
            event=webhook_event,
            active_only=active_only
        )
        
        return {
            "webhooks": [
                {
                    "id": w.id,
                    "url": w.url,
                    "events": [e.value for e in w.events],
                    "active": w.active,
                    "success_count": w.success_count,
                    "failure_count": w.failure_count,
                    "last_triggered": w.last_triggered.isoformat() if w.last_triggered else None,
                    "created_at": w.created_at.isoformat()
                }
                for w in webhooks
            ],
            "total": len(webhooks)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service)
):
    """Get webhook by ID."""
    try:
        webhook = service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {
            "id": webhook.id,
            "url": webhook.url,
            "events": [e.value for e in webhook.events],
            "active": webhook.active,
            "headers": webhook.headers,
            "timeout": webhook.timeout,
            "success_count": webhook.success_count,
            "failure_count": webhook.failure_count,
            "last_triggered": webhook.last_triggered.isoformat() if webhook.last_triggered else None,
            "created_at": webhook.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{webhook_id}/stats")
async def get_webhook_stats(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service)
):
    """Get webhook statistics."""
    try:
        stats = service.get_webhook_stats(webhook_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    request: WebhookUpdateRequest,
    service: WebhookService = Depends(get_webhook_service)
):
    """Update webhook."""
    try:
        events = None
        if request.events:
            events = [WebhookEvent(e) for e in request.events]
        
        webhook = service.update_webhook(
            webhook_id=webhook_id,
            url=request.url,
            events=events,
            active=request.active,
            headers=request.headers,
            timeout=request.timeout
        )
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {
            "id": webhook.id,
            "url": webhook.url,
            "events": [e.value for e in webhook.events],
            "active": webhook.active,
            "updated_at": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid event: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    service: WebhookService = Depends(get_webhook_service)
):
    """Delete webhook."""
    try:
        success = service.delete_webhook(webhook_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {"message": "Webhook deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{webhook_id}")
async def test_webhook(
    webhook_id: str,
    payload: Optional[Dict[str, Any]] = Body(None),
    service: WebhookService = Depends(get_webhook_service)
):
    """Test a webhook with a test event."""
    try:
        webhook = service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        test_payload = payload or {"test": True, "message": "Test webhook"}
        result = await service.trigger_webhook(
            WebhookEvent.QUERY_COMPLETED,  # Use a test event
            test_payload
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""Webhook utilities for REST API integration."""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import httpx
import json
import hashlib
import hmac
import secrets


class WebhookEvent(str, Enum):
    """Webhook event types."""
    QUERY_COMPLETED = "query.completed"
    QUERY_FAILED = "query.failed"
    DATABASE_REGISTERED = "database.registered"
    DATABASE_SYNCED = "database.synced"
    SCHEMA_CHANGED = "schema.changed"
    DASHBOARD_CREATED = "dashboard.created"
    DASHBOARD_UPDATED = "dashboard.updated"
    EXPORT_COMPLETED = "export.completed"


@dataclass
class Webhook:
    """Webhook configuration."""
    id: str
    url: str
    events: List[WebhookEvent]
    secret: str
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30


class WebhookService:
    """Service for managing and triggering webhooks."""
    
    def __init__(self):
        self._webhooks: Dict[str, Webhook] = {}
        self._client = httpx.AsyncClient(timeout=30.0)
    
    @staticmethod
    def _generate_secret() -> str:
        """Generate a secure webhook secret."""
        return secrets.token_urlsafe(32)
    
    def create_webhook(
        self,
        url: str,
        events: List[WebhookEvent],
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> Webhook:
        """Create a new webhook."""
        webhook_id = hashlib.sha256(
            f"{url}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        webhook = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            secret=self._generate_secret(),
            headers=headers or {},
            timeout=timeout
        )
        
        self._webhooks[webhook_id] = webhook
        return webhook
    
    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self._webhooks.get(webhook_id)
    
    def list_webhooks(
        self,
        event: Optional[WebhookEvent] = None,
        active_only: bool = False
    ) -> List[Webhook]:
        """List webhooks."""
        webhooks = list(self._webhooks.values())
        
        if event:
            webhooks = [w for w in webhooks if event in w.events]
        
        if active_only:
            webhooks = [w for w in webhooks if w.active]
        
        return webhooks
    
    def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        active: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Optional[Webhook]:
        """Update webhook."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return None
        
        if url is not None:
            webhook.url = url
        if events is not None:
            webhook.events = events
        if active is not None:
            webhook.active = active
        if headers is not None:
            webhook.headers.update(headers)
        if timeout is not None:
            webhook.timeout = timeout
        
        return webhook
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook."""
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False
    
    async def trigger_webhook(
        self,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger webhooks for an event."""
        results = []
        
        # Find webhooks subscribed to this event
        webhooks = [
            w for w in self._webhooks.values()
            if w.active and event in w.events
        ]
        
        for webhook in webhooks:
            try:
                # Prepare payload
                webhook_payload = {
                    "event": event.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": payload
                }
                
                # Generate signature
                signature = self._generate_signature(
                    webhook.secret,
                    json.dumps(webhook_payload, sort_keys=True)
                )
                
                # Prepare headers
                headers = {
                    **webhook.headers,
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event.value,
                    "Content-Type": "application/json"
                }
                
                # Send webhook
                response = await self._client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers=headers,
                    timeout=webhook.timeout
                )
                
                # Update stats
                webhook.last_triggered = datetime.utcnow()
                if response.is_success:
                    webhook.success_count += 1
                else:
                    webhook.failure_count += 1
                
                results.append({
                    "webhook_id": webhook.id,
                    "url": webhook.url,
                    "status_code": response.status_code,
                    "success": response.is_success
                })
            except Exception as e:
                webhook.failure_count += 1
                results.append({
                    "webhook_id": webhook.id,
                    "url": webhook.url,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "event": event.value,
            "triggered_count": len(webhooks),
            "results": results
        }
    
    @staticmethod
    def _generate_signature(secret: str, payload: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
        """Verify webhook signature."""
        expected = WebhookService._generate_signature(secret, payload)
        return hmac.compare_digest(expected, signature)
    
    def get_webhook_stats(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook statistics."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return None
        
        return {
            "webhook_id": webhook.id,
            "url": webhook.url,
            "active": webhook.active,
            "events": [e.value for e in webhook.events],
            "success_count": webhook.success_count,
            "failure_count": webhook.failure_count,
            "total_count": webhook.success_count + webhook.failure_count,
            "success_rate": (
                webhook.success_count / (webhook.success_count + webhook.failure_count)
                if (webhook.success_count + webhook.failure_count) > 0
                else 0.0
            ),
            "last_triggered": webhook.last_triggered.isoformat() if webhook.last_triggered else None,
            "created_at": webhook.created_at.isoformat()
        }



"""Query result sharing utilities."""
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets
import uuid


@dataclass
class SharedResult:
    """Shared query result entity."""
    share_id: str
    query_id: str
    share_token: str
    expires_at: Optional[datetime] = None
    access_count: int = 0
    max_accesses: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_active: bool = True
    allowed_emails: List[str] = field(default_factory=list)
    password: Optional[str] = None  # Hashed password


class QueryResultSharingService:
    """Service for sharing query results."""
    
    def __init__(self):
        self._shares: Dict[str, SharedResult] = {}  # share_id -> SharedResult
        self._token_lookup: Dict[str, str] = {}  # share_token -> share_id
    
    @staticmethod
    def _generate_token() -> str:
        """Generate a secure share token."""
        return secrets.token_urlsafe(32)
    
    async def create_share(
        self,
        query_id: str,
        expires_in_hours: Optional[int] = None,
        max_accesses: Optional[int] = None,
        created_by: Optional[str] = None,
        allowed_emails: Optional[List[str]] = None,
        password: Optional[str] = None
    ) -> SharedResult:
        """Create a shareable link for a query result."""
        share_id = str(uuid.uuid4())
        share_token = self._generate_token()
        
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        shared_result = SharedResult(
            share_id=share_id,
            query_id=query_id,
            share_token=share_token,
            expires_at=expires_at,
            max_accesses=max_accesses,
            created_by=created_by,
            allowed_emails=allowed_emails or [],
            password=password  # In production, hash this
        )
        
        self._shares[share_id] = shared_result
        self._token_lookup[share_token] = share_id
        
        return shared_result
    
    async def get_share(self, share_token: str, password: Optional[str] = None) -> Optional[SharedResult]:
        """Get shared result by token."""
        share_id = self._token_lookup.get(share_token)
        if not share_id:
            return None
        
        shared_result = self._shares.get(share_id)
        if not shared_result or not shared_result.is_active:
            return None
        
        # Check expiration
        if shared_result.expires_at and shared_result.expires_at < datetime.utcnow():
            return None
        
        # Check max accesses
        if shared_result.max_accesses and shared_result.access_count >= shared_result.max_accesses:
            return None
        
        # Check password
        if shared_result.password and shared_result.password != password:
            return None
        
        # Increment access count
        shared_result.access_count += 1
        
        return shared_result
    
    async def revoke_share(self, share_id: str) -> bool:
        """Revoke a shared result."""
        if share_id in self._shares:
            self._shares[share_id].is_active = False
            return True
        return False
    
    async def delete_share(self, share_id: str) -> bool:
        """Delete a shared result."""
        if share_id in self._shares:
            shared_result = self._shares[share_id]
            # Remove from token lookup
            if shared_result.share_token in self._token_lookup:
                del self._token_lookup[shared_result.share_token]
            del self._shares[share_id]
            return True
        return False
    
    async def list_shares(
        self,
        created_by: Optional[str] = None,
        query_id: Optional[str] = None
    ) -> List[SharedResult]:
        """List shared results."""
        shares = list(self._shares.values())
        
        if created_by:
            shares = [s for s in shares if s.created_by == created_by]
        
        if query_id:
            shares = [s for s in shares if s.query_id == query_id]
        
        return shares
    
    def get_share_url(self, share_token: str, base_url: str = "http://localhost:8000") -> str:
        """Generate shareable URL."""
        return f"{base_url}/api/shared/{share_token}"



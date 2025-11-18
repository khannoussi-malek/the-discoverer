"""API key management for authentication."""
import secrets
import hashlib
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class APIKey:
    """API key entity."""
    id: str
    key_hash: str  # Hashed version of the key
    name: str
    user_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)  # e.g., ["read", "write", "admin"]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    rate_limit: Optional[int] = None  # Requests per minute
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIKeyManager:
    """Manage API keys for authentication."""
    
    def __init__(self):
        self._keys: Dict[str, APIKey] = {}  # key_id -> APIKey
        self._key_lookup: Dict[str, str] = {}  # key_hash -> key_id
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def _generate_key(prefix: str = "dk_") -> str:
        """Generate a new API key."""
        # Generate 32 random bytes and encode as base64-like string
        random_bytes = secrets.token_bytes(32)
        key_part = secrets.token_urlsafe(32)
        return f"{prefix}{key_part}"
    
    async def create_key(
        self,
        name: str,
        user_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[str, APIKey]:
        """Create a new API key. Returns (key, APIKey entity)."""
        # Generate key
        key = self._generate_key()
        key_hash = self._hash_key(key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create entity
        api_key = APIKey(
            id=secrets.token_urlsafe(16),
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            scopes=scopes or ["read", "write"],
            expires_at=expires_at,
            rate_limit=rate_limit,
            metadata=metadata or {}
        )
        
        # Store
        self._keys[api_key.id] = api_key
        self._key_lookup[key_hash] = api_key.id
        
        return key, api_key
    
    async def validate_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key and return the entity if valid."""
        key_hash = self._hash_key(key)
        key_id = self._key_lookup.get(key_hash)
        
        if not key_id:
            return None
        
        api_key = self._keys.get(key_id)
        if not api_key:
            return None
        
        # Check if active
        if not api_key.is_active:
            return None
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        
        return api_key
    
    async def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id in self._keys:
            self._keys[key_id].is_active = False
            return True
        return False
    
    async def delete_key(self, key_id: str) -> bool:
        """Delete an API key permanently."""
        if key_id in self._keys:
            api_key = self._keys[key_id]
            # Remove from lookup
            if api_key.key_hash in self._key_lookup:
                del self._key_lookup[api_key.key_hash]
            del self._keys[key_id]
            return True
        return False
    
    async def get_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        return self._keys.get(key_id)
    
    async def list_keys(
        self,
        user_id: Optional[str] = None,
        active_only: bool = False
    ) -> List[APIKey]:
        """List API keys."""
        keys = list(self._keys.values())
        
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        
        if active_only:
            keys = [k for k in keys if k.is_active]
            # Also filter expired
            now = datetime.utcnow()
            keys = [k for k in keys if not k.expires_at or k.expires_at > now]
        
        return keys
    
    async def update_key(
        self,
        key_id: str,
        name: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        rate_limit: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[APIKey]:
        """Update API key properties."""
        api_key = self._keys.get(key_id)
        if not api_key:
            return None
        
        if name is not None:
            api_key.name = name
        if scopes is not None:
            api_key.scopes = scopes
        if is_active is not None:
            api_key.is_active = is_active
        if rate_limit is not None:
            api_key.rate_limit = rate_limit
        if metadata is not None:
            api_key.metadata.update(metadata)
        
        return api_key
    
    def has_scope(self, api_key: APIKey, scope: str) -> bool:
        """Check if API key has a specific scope."""
        return scope in api_key.scopes or "admin" in api_key.scopes


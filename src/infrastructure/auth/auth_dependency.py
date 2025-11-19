"""Unified authentication dependency for JWT tokens and API keys."""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.infrastructure.auth.jwt_auth import jwt_auth
from src.infrastructure.auth.api_key_manager import APIKeyManager


security = HTTPBearer(auto_error=False)


async def get_api_key_manager() -> APIKeyManager:
    """Dependency injection for API key manager."""
    from src.api.main import app
    if not hasattr(app.state, 'api_key_manager'):
        from src.infrastructure.auth.api_key_manager import APIKeyManager
        app.state.api_key_manager = APIKeyManager()
    return app.state.api_key_manager


class AuthInfo:
    """Authentication information."""
    def __init__(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        roles: Optional[list] = None,
        api_key: Optional[Any] = None,
        auth_type: str = "none"  # "jwt", "api_key", "none"
    ):
        self.user_id = user_id
        self.username = username
        self.roles = roles or []
        self.api_key = api_key
        self.auth_type = auth_type
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.auth_type in ("jwt", "api_key")
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles or "admin" in self.roles
    
    def has_scope(self, scope: str) -> bool:
        """Check if API key has a specific scope."""
        if self.api_key:
            return scope in self.api_key.scopes or "admin" in self.api_key.scopes
        return False


async def get_current_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_manager: APIKeyManager = Depends(get_api_key_manager)
) -> AuthInfo:
    """
    Unified authentication dependency.
    Accepts either JWT Bearer token or X-API-Key header.
    """
    # Try JWT token first
    if credentials and credentials.credentials:
        try:
            payload = jwt_auth.verify_token(credentials.credentials)
            return AuthInfo(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                roles=payload.get("roles", []),
                auth_type="jwt"
            )
        except HTTPException:
            # If JWT fails, try API key
            pass
    
    # Try API key
    if x_api_key:
        api_key = await api_key_manager.validate_key(x_api_key)
        if api_key:
            return AuthInfo(
                user_id=api_key.user_id,
                api_key=api_key,
                auth_type="api_key"
            )
    
    # No valid authentication found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide either a Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_manager: APIKeyManager = Depends(get_api_key_manager)
) -> AuthInfo:
    """
    Optional authentication dependency.
    Returns AuthInfo even if not authenticated (for public endpoints that can be enhanced with auth).
    """
    # Try JWT token first
    if credentials and credentials.credentials:
        try:
            payload = jwt_auth.verify_token(credentials.credentials)
            return AuthInfo(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                roles=payload.get("roles", []),
                auth_type="jwt"
            )
        except HTTPException:
            pass
    
    # Try API key
    if x_api_key:
        api_key = await api_key_manager.validate_key(x_api_key)
        if api_key:
            return AuthInfo(
                user_id=api_key.user_id,
                api_key=api_key,
                auth_type="api_key"
            )
    
    # Return unauthenticated info
    return AuthInfo(auth_type="none")


async def require_auth(auth: AuthInfo = Depends(get_current_auth)) -> AuthInfo:
    """Require authentication - raises 401 if not authenticated."""
    if not auth.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return auth


async def require_role(role: str):
    """Dependency factory to require a specific role."""
    async def _require_role(auth: AuthInfo = Depends(require_auth)) -> AuthInfo:
        if not auth.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return auth
    return _require_role


async def require_scope(scope: str):
    """Dependency factory to require a specific API key scope."""
    async def _require_scope(auth: AuthInfo = Depends(require_auth)) -> AuthInfo:
        if auth.auth_type == "api_key" and not auth.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{scope}' required"
            )
        return auth
    return _require_scope


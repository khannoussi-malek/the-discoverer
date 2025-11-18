"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from src.infrastructure.auth.user_repository import UserRepository, User
from src.infrastructure.auth.jwt_auth import jwt_auth


router = APIRouter(prefix="/api/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    """User registration request."""
    username: str
    email: EmailStr
    password: str
    roles: Optional[List[str]] = None


class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response."""
    id: str
    username: str
    email: str
    roles: List[str]
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


security = HTTPBearer()


def get_user_repository() -> UserRepository:
    """Dependency injection for user repository."""
    from src.api.main import app
    return app.state.user_repository


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    repository: UserRepository = Depends(get_user_repository)
):
    """Register a new user."""
    try:
        user = await repository.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            roles=request.roles
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    repository: UserRepository = Depends(get_user_repository)
):
    """Login and get access token."""
    user = await repository.authenticate(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate token
    token = jwt_auth.create_token(
        user_id=user.id,
        username=user.username,
        roles=user.roles
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repository: UserRepository = Depends(get_user_repository)
):
    """Get current authenticated user."""
    try:
        payload = jwt_auth.verify_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        user = await repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    repository: UserRepository = Depends(get_user_repository),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List all users (admin only)."""
    # Verify token and check admin role
    try:
        payload = jwt_auth.verify_token(credentials.credentials)
        if "admin" not in payload.get("roles", []):
            raise HTTPException(status_code=403, detail="Admin access required")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    users = await repository.list_users()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        for user in users
    ]



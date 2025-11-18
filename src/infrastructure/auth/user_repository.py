"""User repository."""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import hashlib


class User:
    """User entity."""
    def __init__(
        self,
        id: str,
        username: str,
        email: str,
        password_hash: str,
        roles: List[str] = None,
        created_at: datetime = None,
        last_login: datetime = None,
        is_active: bool = True
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.roles = roles or []
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.is_active = is_active


class UserRepository:
    """User repository - in-memory implementation."""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._users_by_username: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256 (simple, should use bcrypt in production)."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: List[str] = None
    ) -> User:
        """Create a new user."""
        if username in self._users_by_username:
            raise ValueError(f"Username '{username}' already exists")
        if email in self._users_by_email:
            raise ValueError(f"Email '{email}' already exists")
        
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            roles=roles or ["user"],
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        self._users[user.id] = user
        self._users_by_username[username] = user
        self._users_by_email[email] = user
        
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self._users_by_username.get(username)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self._users_by_email.get(email)
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = await self.get_by_username(username)
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        password_hash = self._hash_password(password)
        if user.password_hash != password_hash:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        return user
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user."""
        user = self._users.get(user_id)
        if not user:
            return None
        
        # Update fields
        if "email" in updates:
            # Remove old email mapping
            if user.email in self._users_by_email:
                del self._users_by_email[user.email]
            # Add new email mapping
            user.email = updates["email"]
            self._users_by_email[user.email] = user
        
        if "password" in updates:
            user.password_hash = self._hash_password(updates["password"])
        
        if "roles" in updates:
            user.roles = updates["roles"]
        
        if "is_active" in updates:
            user.is_active = updates["is_active"]
        
        return user
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List users."""
        users = list(self._users.values())
        return users[offset:offset + limit]
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        user = self._users.get(user_id)
        if not user:
            return False
        
        # Remove from all mappings
        del self._users[user_id]
        if user.username in self._users_by_username:
            del self._users_by_username[user.username]
        if user.email in self._users_by_email:
            del self._users_by_email[user.email]
        
        return True



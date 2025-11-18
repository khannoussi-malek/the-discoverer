"""Database repository - Repository pattern."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from src.domain.database import Database


class DatabaseRepository(ABC):
    """Repository interface - KISS: Simple abstraction."""
    
    @abstractmethod
    async def get_all(self) -> List[Database]:
        """Get all databases."""
        pass
    
    @abstractmethod
    async def get_by_id(self, db_id: str) -> Optional[Database]:
        """Get database by ID."""
        pass
    
    @abstractmethod
    async def save(self, database: Database) -> None:
        """Save database."""
        pass
    
    @abstractmethod
    async def delete(self, db_id: str) -> None:
        """Delete database."""
        pass


class InMemoryDatabaseRepository(DatabaseRepository):
    """Simple in-memory implementation."""
    
    def __init__(self):
        self._databases: Dict[str, Database] = {}
    
    async def get_all(self) -> List[Database]:
        """Get all databases."""
        return list(self._databases.values())
    
    async def get_by_id(self, db_id: str) -> Optional[Database]:
        """Get database by ID."""
        return self._databases.get(db_id)
    
    async def save(self, database: Database) -> None:
        """Save database."""
        self._databases[database.id] = database
    
    async def delete(self, db_id: str) -> None:
        """Delete database."""
        if db_id in self._databases:
            del self._databases[db_id]


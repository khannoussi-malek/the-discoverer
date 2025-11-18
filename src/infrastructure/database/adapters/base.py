"""Base database adapter interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.domain.schema import Schema


class DatabaseAdapter(ABC):
    """Base adapter - KISS: Simple interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize adapter with configuration."""
        self.config = config
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection."""
        pass
    
    @abstractmethod
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract database schema."""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute query and return results."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection works."""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected."""
        return self._connected
    
    async def get_sample_data(
        self, 
        table: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from table (optional, for content indexing)."""
        raise NotImplementedError("Sample data extraction not implemented")


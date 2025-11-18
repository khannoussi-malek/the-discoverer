"""Database domain entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from src.domain.schema import Schema


@dataclass(frozen=True)
class Database:
    """Database entity - KISS: Simple data class."""
    
    id: str
    type: str  # "postgresql", "mongodb", "mysql", "cassandra", "elasticsearch"
    name: str
    host: str
    port: int
    database_name: str
    schema: Optional[Schema] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_synced: Optional[datetime] = None
    connection_pool_size: int = 10
    is_active: bool = True


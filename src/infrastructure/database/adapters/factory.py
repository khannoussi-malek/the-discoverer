"""Database adapter factory."""
from typing import Dict, Type, List

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.infrastructure.database.adapters.postgresql import PostgreSQLAdapter
from src.infrastructure.database.adapters.mongodb import MongoDBAdapter
from src.infrastructure.database.adapters.mysql import MySQLAdapter
from src.infrastructure.database.adapters.sqlite import SQLiteAdapter
from src.infrastructure.database.adapters.cassandra import CassandraAdapter
from src.infrastructure.database.adapters.elasticsearch import ElasticsearchAdapter


class DatabaseAdapterFactory:
    """Factory - KISS: Simple creation logic."""
    
    _adapters: Dict[str, Type[DatabaseAdapter]] = {
        "postgresql": PostgreSQLAdapter,
        "mongodb": MongoDBAdapter,
        "mysql": MySQLAdapter,
        "sqlite": SQLiteAdapter,
        "cassandra": CassandraAdapter,
        "elasticsearch": ElasticsearchAdapter,
    }
    
    @classmethod
    def create(cls, db_type: str, config: Dict) -> DatabaseAdapter:
        """Create adapter based on type - DRY: No duplication."""
        adapter_class = cls._adapters.get(db_type.lower())
        if not adapter_class:
            raise ValueError(f"Unsupported database type: {db_type}")
        return adapter_class(config)
    
    @classmethod
    def register(cls, db_type: str, adapter_class: Type[DatabaseAdapter]) -> None:
        """Extend without modifying - Open/Closed Principle."""
        cls._adapters[db_type.lower()] = adapter_class
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of supported database types."""
        return list(cls._adapters.keys())


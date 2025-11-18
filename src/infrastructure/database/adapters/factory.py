"""Database adapter factory."""
from typing import Dict, Type, List, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter


def _lazy_import_adapter(adapter_name: str) -> Optional[Type[DatabaseAdapter]]:
    """Lazy import adapter to avoid import errors if dependencies are missing."""
    try:
        if adapter_name == "postgresql":
            from src.infrastructure.database.adapters.postgresql import PostgreSQLAdapter
            return PostgreSQLAdapter
        elif adapter_name == "mongodb":
            from src.infrastructure.database.adapters.mongodb import MongoDBAdapter
            return MongoDBAdapter
        elif adapter_name == "mysql":
            from src.infrastructure.database.adapters.mysql import MySQLAdapter
            return MySQLAdapter
        elif adapter_name == "sqlite":
            from src.infrastructure.database.adapters.sqlite import SQLiteAdapter
            return SQLiteAdapter
        elif adapter_name == "cassandra":
            from src.infrastructure.database.adapters.cassandra import CassandraAdapter
            return CassandraAdapter
        elif adapter_name == "elasticsearch":
            from src.infrastructure.database.adapters.elasticsearch import ElasticsearchAdapter
            return ElasticsearchAdapter
    except ImportError:
        return None
    return None


class DatabaseAdapterFactory:
    """Factory - KISS: Simple creation logic."""
    
    _adapters: Dict[str, Type[DatabaseAdapter]] = {}
    
    @classmethod
    def _get_adapters(cls) -> Dict[str, Type[DatabaseAdapter]]:
        """Get adapters with lazy loading."""
        if not cls._adapters:
            for name in ["postgresql", "mongodb", "mysql", "sqlite", "cassandra", "elasticsearch"]:
                adapter = _lazy_import_adapter(name)
                if adapter:
                    cls._adapters[name] = adapter
        return cls._adapters
    
    @classmethod
    def create(cls, db_type: str, config: Dict) -> DatabaseAdapter:
        """Create adapter based on type - DRY: No duplication."""
        adapters = cls._get_adapters()
        adapter_class = adapters.get(db_type.lower())
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
        return list(cls._get_adapters().keys())


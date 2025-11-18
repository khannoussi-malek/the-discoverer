"""Discovery service - Business logic for database discovery."""
from typing import Dict, Any
from datetime import datetime

from src.domain.database import Database
from src.domain.schema import Schema
from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory
from src.infrastructure.vector_db.schema_indexer import SchemaIndexer
from src.infrastructure.cache.repository import CacheRepository
from src.infrastructure.database.validators import (
    validate_database_config,
    validate_database_connection
)
from src.core.exceptions import DatabaseConnectionError, SchemaExtractionError


class DiscoveryService:
    """Discovery service - KISS: One responsibility."""
    
    def __init__(
        self,
        db_repository: DatabaseRepository,
        schema_indexer: SchemaIndexer,
        cache: CacheRepository
    ):
        self.db_repository = db_repository
        self.schema_indexer = schema_indexer
        self.cache = cache
    
    async def discover_database(self, config: Dict[str, Any]) -> Database:
        """
        Discover and register a database.
        
        Steps:
        1. Validate config
        2. Validate connection
        3. Create adapter
        4. Extract schema
        5. Index schema to vector DB
        6. Save to repository
        7. Cache schema
        """
        # Validate configuration
        errors = validate_database_config(config)
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Validate connection
        await validate_database_connection(config)
        
        # Create adapter
        adapter = DatabaseAdapterFactory.create(config["type"], config)
        
        # Connect and extract schema
        await adapter.connect()
        
        try:
            # Extract schema
            schema = await adapter.extract_schema(config["id"])
        except Exception as e:
            await adapter.disconnect()
            raise SchemaExtractionError(
                f"Failed to extract schema: {str(e)}",
                database_id=config["id"]
            )
        
        # Index to vector DB
        try:
            await self.schema_indexer.index_schema(config["id"], schema)
        except Exception as e:
            # Log error but continue - schema extraction succeeded
            pass
        
        # Create domain entity
        database = Database(
            id=config["id"],
            type=config["type"],
            name=config.get("name", config["id"]),
            host=config["host"],
            port=config["port"],
            database_name=config["database"],
            schema=schema,
            config=config,
            metadata=config.get("metadata", {}),
            last_synced=datetime.now()
        )
        
        # Save
        await self.db_repository.save(database)
        
        # Cache schema
        await self.cache.set(
            f"schema:{config['id']}",
            schema,
            ttl=3600
        )
        
        # Disconnect
        await adapter.disconnect()
        
        return database
    
    async def sync_schema(self, db_id: str) -> Schema:
        """Incremental schema sync - only update changed tables."""
        database = await self.db_repository.get_by_id(db_id)
        if not database:
            raise ValueError(f"Database {db_id} not found")
        
        adapter = DatabaseAdapterFactory.create(database.type, database.config)
        await adapter.connect()
        
        new_schema = await adapter.extract_schema(db_id)
        
        # Compare with existing
        if database.schema:
            changes = self._detect_schema_changes(database.schema, new_schema)
            if changes:
                # Only re-index changed tables
                await self.schema_indexer.update_schema(db_id, changes)
        
        # Update database
        updated_db = Database(
            id=database.id,
            type=database.type,
            name=database.name,
            host=database.host,
            port=database.port,
            database_name=database.database_name,
            schema=new_schema,
            config=database.config,
            metadata=database.metadata,
            created_at=database.created_at,
            last_synced=datetime.now(),
            connection_pool_size=database.connection_pool_size,
            is_active=database.is_active
        )
        await self.db_repository.save(updated_db)
        
        # Update cache
        await self.cache.set(f"schema:{db_id}", new_schema, ttl=3600)
        
        await adapter.disconnect()
        
        return new_schema
    
    
    def _detect_schema_changes(
        self,
        old: Schema,
        new: Schema
    ) -> Dict[str, Any]:
        """Detect what changed between schemas."""
        changes = {
            "added_tables": [],
            "removed_tables": [],
            "modified_tables": []
        }
        
        old_table_names = {t.name for t in old.tables}
        new_table_names = {t.name for t in new.tables}
        
        changes["added_tables"] = list(new_table_names - old_table_names)
        changes["removed_tables"] = list(old_table_names - new_table_names)
        
        # Check modified tables
        for new_table in new.tables:
            if new_table.name in old_table_names:
                old_table = next(t for t in old.tables if t.name == new_table.name)
                if old_table != new_table:
                    changes["modified_tables"].append(new_table.name)
        
        return changes


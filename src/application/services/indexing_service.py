"""Indexing service - Content indexing."""
from typing import List, Dict, Any

from src.infrastructure.vector_db.content_indexer import ContentIndexer
from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory


class IndexingService:
    """Indexing service - KISS: One responsibility."""
    
    def __init__(
        self,
        content_indexer: ContentIndexer,
        db_repository: DatabaseRepository
    ):
        self.content_indexer = content_indexer
        self.db_repository = db_repository
    
    async def index_table_content(
        self,
        db_id: str,
        table: str,
        strategy: str = "smart"
    ) -> None:
        """Index table content to vector DB."""
        # Get database
        database = await self.db_repository.get_by_id(db_id)
        if not database:
            raise ValueError(f"Database {db_id} not found")
        
        # Create adapter
        adapter = DatabaseAdapterFactory.create(database.type, database.config)
        await adapter.connect()
        
        try:
            # Get sample data
            sample_data = await adapter.get_sample_data(table, limit=10000)
            
            # Index to vector DB
            await self.content_indexer.index_table_content(
                db_id=db_id,
                table=table,
                data=sample_data,
                strategy=strategy
            )
        finally:
            await adapter.disconnect()


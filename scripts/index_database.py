"""Script to index a database schema."""
import asyncio
import sys
from src.application.services.discovery_service import DiscoveryService
from src.infrastructure.database.repository import InMemoryDatabaseRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.vector_db.schema_indexer import SchemaIndexer
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from src.infrastructure.cache.repository import MultiLayerCacheRepository


async def main():
    """Index database from config."""
    if len(sys.argv) < 2:
        print("Usage: python index_database.py <database_id>")
        sys.exit(1)
    
    db_id = sys.argv[1]
    
    # Initialize services
    db_repository = InMemoryDatabaseRepository()
    vector_db_client = QdrantVectorDBClient()
    embedding_generator = EmbeddingGenerator()
    schema_indexer = SchemaIndexer(vector_db_client, embedding_generator)
    cache = MultiLayerCacheRepository()
    
    discovery_service = DiscoveryService(db_repository, schema_indexer, cache)
    
    # Get database from repository
    database = await db_repository.get_by_id(db_id)
    if not database:
        print(f"Database {db_id} not found!")
        sys.exit(1)
    
    # Sync schema
    await discovery_service.sync_schema(db_id)
    print(f"Database {db_id} indexed successfully!")


if __name__ == "__main__":
    asyncio.run(main())


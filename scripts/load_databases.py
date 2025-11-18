"""Script to load databases from configuration file."""
import asyncio
import sys
from src.utils.config_loader import load_database_configs
from src.application.services.discovery_service import DiscoveryService
from src.infrastructure.database.repository import InMemoryDatabaseRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.vector_db.schema_indexer import SchemaIndexer
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from src.infrastructure.cache.repository import MultiLayerCacheRepository


async def main():
    """Load and register databases from config file."""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config/databases.yaml"
    
    # Load configurations
    configs = load_database_configs(config_path)
    
    if not configs:
        print(f"No databases found in {config_path}")
        return
    
    # Initialize services
    db_repository = InMemoryDatabaseRepository()
    vector_db_client = QdrantVectorDBClient()
    embedding_generator = EmbeddingGenerator()
    schema_indexer = SchemaIndexer(vector_db_client, embedding_generator)
    cache = MultiLayerCacheRepository()
    
    discovery_service = DiscoveryService(db_repository, schema_indexer, cache)
    
    # Initialize vector DB
    await vector_db_client.initialize_collections()
    
    # Register each database
    for config in configs:
        try:
            print(f"Registering database: {config.get('id', 'unknown')}...")
            database = await discovery_service.discover_database(config)
            print(f"✓ Successfully registered: {database.id}")
        except Exception as e:
            print(f"✗ Failed to register {config.get('id', 'unknown')}: {str(e)}")
    
    print(f"\nRegistered {len(configs)} database(s)")


if __name__ == "__main__":
    asyncio.run(main())


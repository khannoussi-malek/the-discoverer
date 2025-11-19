"""Integration tests for vector database."""
import pytest
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from config.settings import get_settings

# Check if sentence-transformers is available
try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


@pytest.mark.integration
class TestQdrantVectorDB:
    """Integration tests for Qdrant."""
    
    @pytest.fixture
    def vector_db_client(self):
        """Vector DB client fixture."""
        return QdrantVectorDBClient()
    
    @pytest.fixture
    def embedding_generator(self):
        """Embedding generator fixture."""
        return EmbeddingGenerator()
    
    @pytest.mark.asyncio
    async def test_initialize_collections(self, vector_db_client):
        """Test collection initialization."""
        await vector_db_client.initialize_collections()
        # Should not raise exception
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not SENTENCE_TRANSFORMERS_AVAILABLE, reason="sentence-transformers not available in CI")
    async def test_search(self, vector_db_client, embedding_generator):
        """Test vector search."""
        settings = get_settings()
        
        # Generate test embedding
        query_embedding = await embedding_generator.generate("test query")
        
        # Search
        results = await vector_db_client.search(
            collection_name=settings.qdrant_collection_schemas,
            query_vector=query_embedding,
            limit=5
        )
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_batch_upsert(self, vector_db_client):
        """Test batch upsert."""
        settings = get_settings()
        
        # Create test points
        points = [
            {
                "id": "test_1",
                "vector": [0.1] * 384,
                "payload": {"test": "data1"}
            },
            {
                "id": "test_2",
                "vector": [0.2] * 384,
                "payload": {"test": "data2"}
            }
        ]
        
        await vector_db_client.batch_upsert(
            collection_name=settings.qdrant_collection_schemas,
            points=points
        )
        
        # Verify by searching
        results = await vector_db_client.search(
            collection_name=settings.qdrant_collection_schemas,
            query_vector=[0.1] * 384,
            limit=10
        )
        
        assert len(results) > 0



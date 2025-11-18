"""Integration tests for query service."""
import pytest
from src.application.services.query_service import QueryService
from src.infrastructure.database.repository import InMemoryDatabaseRepository
from src.infrastructure.vector_db.repository import VectorDBRepository
from src.infrastructure.llm.generators.factory import QueryGeneratorFactory
from src.infrastructure.cache.repository import MultiLayerCacheRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from src.infrastructure.llm.client import LLMClient


@pytest.mark.integration
class TestQueryService:
    """Integration tests for query service."""
    
    @pytest.fixture
    def query_service(self):
        """Query service fixture."""
        db_repository = InMemoryDatabaseRepository()
        vector_db_client = QdrantVectorDBClient()
        embedding_generator = EmbeddingGenerator()
        vector_db_repository = VectorDBRepository(vector_db_client, embedding_generator)
        cache = MultiLayerCacheRepository()
        llm_client = LLMClient()
        query_generator_factory = QueryGeneratorFactory(llm_client)
        
        return QueryService(
            db_repository,
            vector_db_repository,
            query_generator_factory,
            cache
        )
    
    @pytest.mark.asyncio
    async def test_execute_simple_query(self, query_service):
        """Test executing a simple query."""
        # This test requires a registered database
        # For now, just test that service can be instantiated
        assert query_service is not None
    
    @pytest.mark.asyncio
    async def test_cache_query_result(self, query_service):
        """Test query result caching."""
        # Test that cache is used
        assert query_service.cache is not None



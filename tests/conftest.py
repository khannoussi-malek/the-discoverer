"""Pytest configuration and fixtures."""
import pytest
import asyncio
from src.infrastructure.database.repository import InMemoryDatabaseRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from src.infrastructure.cache.repository import MultiLayerCacheRepository
from src.infrastructure.llm.client import LLMClient


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_repository():
    """Database repository fixture."""
    return InMemoryDatabaseRepository()


@pytest.fixture
def cache_repository():
    """Cache repository fixture."""
    return MultiLayerCacheRepository()


@pytest.fixture
def embedding_generator():
    """Embedding generator fixture."""
    return EmbeddingGenerator()


@pytest.fixture
def llm_client():
    """LLM client fixture."""
    return LLMClient()


@pytest.fixture
def vector_db_client():
    """Vector DB client fixture."""
    return QdrantVectorDBClient()


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

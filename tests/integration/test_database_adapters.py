"""Integration tests for database adapters."""
import pytest
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory


@pytest.mark.integration
class TestPostgreSQLAdapter:
    """Integration tests for PostgreSQL adapter."""
    
    @pytest.fixture
    def postgres_config(self):
        """PostgreSQL test configuration."""
        return {
            "id": "test_postgres",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
    
    @pytest.mark.asyncio
    async def test_connection(self, postgres_config):
        """Test PostgreSQL connection."""
        adapter = DatabaseAdapterFactory.create("postgresql", postgres_config)
        try:
            await adapter.connect()
            is_connected = await adapter.test_connection()
            assert is_connected
        finally:
            await adapter.disconnect()
    
    @pytest.mark.asyncio
    async def test_extract_schema(self, postgres_config):
        """Test schema extraction."""
        adapter = DatabaseAdapterFactory.create("postgresql", postgres_config)
        try:
            await adapter.connect()
            schema = await adapter.extract_schema("test_postgres")
            assert schema is not None
            assert len(schema.tables) >= 0
        finally:
            await adapter.disconnect()


@pytest.mark.integration
class TestMongoDBAdapter:
    """Integration tests for MongoDB adapter."""
    
    @pytest.fixture
    def mongodb_config(self):
        """MongoDB test configuration."""
        return {
            "id": "test_mongodb",
            "host": "localhost",
            "port": 27017,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password"
        }
    
    @pytest.mark.asyncio
    async def test_connection(self, mongodb_config):
        """Test MongoDB connection."""
        adapter = DatabaseAdapterFactory.create("mongodb", mongodb_config)
        try:
            await adapter.connect()
            is_connected = await adapter.test_connection()
            assert is_connected
        finally:
            await adapter.disconnect()


@pytest.mark.integration
class TestDatabaseAdapterFactory:
    """Test database adapter factory."""
    
    def test_get_supported_types(self):
        """Test getting supported database types."""
        types = DatabaseAdapterFactory.get_supported_types()
        assert "postgresql" in types
        assert "mongodb" in types
        assert "mysql" in types
        assert "sqlite" in types
        assert "cassandra" in types
    
    def test_create_unsupported_type(self):
        """Test creating unsupported adapter raises error."""
        with pytest.raises(ValueError):
            DatabaseAdapterFactory.create("unsupported", {})



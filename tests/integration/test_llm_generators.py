"""Integration tests for LLM query generators."""
import pytest
from src.infrastructure.llm.client import LLMClient
from src.infrastructure.llm.generators.sql_generator import SQLGenerator
from src.infrastructure.llm.generators.mongodb_generator import MongoDBGenerator
from src.infrastructure.llm.generators.cql_generator import CQLGenerator


@pytest.mark.integration
class TestQueryGenerators:
    """Integration tests for query generators."""
    
    @pytest.fixture
    def llm_client(self):
        """LLM client fixture."""
        return LLMClient()
    
    @pytest.fixture
    def sql_generator(self, llm_client):
        """SQL generator fixture."""
        return SQLGenerator(llm_client)
    
    @pytest.fixture
    def mongodb_generator(self, llm_client):
        """MongoDB generator fixture."""
        return MongoDBGenerator(llm_client)
    
    @pytest.mark.asyncio
    async def test_sql_generator_simple_pattern(self, sql_generator):
        """Test SQL generator pattern matching."""
        schema_context = [
            {
                "payload": {
                    "type": "table",
                    "table_name": "users",
                    "database_id": "test_db"
                }
            }
        ]
        
        query = await sql_generator.generate("count users", schema_context)
        
        assert query.query_type == "sql"
        assert "COUNT" in query.generated_query.upper()
        assert query.confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_mongodb_generator_simple_pattern(self, mongodb_generator):
        """Test MongoDB generator pattern matching."""
        schema_context = [
            {
                "payload": {
                    "type": "table",
                    "table_name": "users",
                    "database_id": "test_db"
                }
            }
        ]
        
        query = await mongodb_generator.generate("count users", schema_context)
        
        assert query.query_type == "mongodb"
        assert "collection" in query.generated_query.lower()
        assert query.confidence > 0.8



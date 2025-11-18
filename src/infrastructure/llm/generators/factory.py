"""Query generator factory."""
from typing import Dict, Type

from src.infrastructure.llm.generators.base import QueryGenerator
from src.infrastructure.llm.generators.sql_generator import SQLGenerator
from src.infrastructure.llm.generators.mongodb_generator import MongoDBGenerator
from src.infrastructure.llm.generators.cql_generator import CQLGenerator
from src.infrastructure.llm.generators.elasticsearch_generator import ElasticsearchGenerator
from src.infrastructure.llm.client import LLMClient


class QueryGeneratorFactory:
    """Factory for query generators - Strategy pattern."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self._generators: Dict[str, Type[QueryGenerator]] = {
            "postgresql": SQLGenerator,
            "mysql": SQLGenerator,
            "sqlite": SQLGenerator,
            "mongodb": MongoDBGenerator,
            "cassandra": CQLGenerator,
            "elasticsearch": ElasticsearchGenerator,
        }
    
    def create(self, db_type: str) -> QueryGenerator:
        """Create generator based on database type."""
        generator_class = self._generators.get(db_type.lower())
        if not generator_class:
            raise ValueError(f"No generator for database type: {db_type}")
        return generator_class(self.llm_client)
    
    def register(self, db_type: str, generator_class: Type[QueryGenerator]) -> None:
        """Register new generator type."""
        self._generators[db_type.lower()] = generator_class


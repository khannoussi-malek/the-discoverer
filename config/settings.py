"""Application settings using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings - Singleton pattern."""
    
    # Application
    app_name: str = "The Discoverer"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Vector Database (Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_schemas: str = "schemas"
    qdrant_collection_content: str = "content"
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_model_complex: str = "gpt-4"
    openai_temperature: float = 0.0
    openai_max_tokens: int = 1000
    
    # Redis Cache
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: str = ""
    cache_ttl: int = 600
    
    # Database Connection Pool
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    db_pool_max_queries: int = 50000
    db_query_timeout: int = 5
    
    # Performance Settings
    max_concurrent_queries: int = 10
    vector_search_limit: int = 20
    vector_search_threshold: float = 0.7
    batch_embedding_size: int = 100
    
    # Security
    secret_key: str = "change-me-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton - DRY: Single source of truth."""
    return Settings()


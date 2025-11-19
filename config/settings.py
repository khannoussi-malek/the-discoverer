"""Application settings using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
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
    llm_provider: str = "openai"  # "openai" or "perplexity"
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_model_complex: str = "gpt-4"
    openai_temperature: float = 0.0
    openai_max_tokens: int = 1000
    
    # Perplexity Configuration
    perplexity_api_key: str = ""
    perplexity_model: str = "sonar"  # Valid models: "sonar", "sonar-pro", "llama-3.1-sonar-large-128k-online" (check docs)
    perplexity_model_complex: str = "sonar-pro"  # Use "sonar-pro" for more capable model
    perplexity_base_url: str = "https://api.perplexity.ai"
    
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
    allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://localhost:5173"
    
    # Default Admin User
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    default_admin_email: str = "admin@discoverer.local"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    api_base_url: str = "http://localhost:8000"
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    
    # Query History
    query_history_max_size: int = 1000
    
    # Health Monitoring
    health_check_interval: int = 30  # seconds
    
    # Scheduler
    scheduler_check_interval: int = 60  # seconds
    scheduled_export_check_interval: int = 60  # seconds
    
    # Webhooks
    webhook_timeout: float = 30.0  # seconds
    webhook_max_retries: int = 3
    
    # Connection Pool Defaults
    pool_default_timeout: float = 30.0  # seconds
    
    # Vector DB Client
    qdrant_client_timeout: float = 5.0  # seconds
    
    # Export Storage
    export_storage_path: str = "/tmp/exports"
    
    # HTTP Client Defaults
    http_client_timeout: float = 30.0  # seconds
    http_client_connect_timeout: float = 5.0  # seconds
    
    # CLI Defaults
    cli_timeout: float = 60.0  # seconds
    cli_health_check_timeout: float = 5.0  # seconds
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get settings singleton - DRY: Single source of truth."""
    return Settings()


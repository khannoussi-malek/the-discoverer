"""FastAPI application main."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware.request_id import RequestIDMiddleware
from src.infrastructure.query_history.repository import QueryHistoryRepository
from src.infrastructure.database.health_monitor import DatabaseHealthMonitor

from config.settings import get_settings
from src.infrastructure.database.repository import InMemoryDatabaseRepository
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.vector_db.schema_indexer import SchemaIndexer
from src.infrastructure.vector_db.repository import VectorDBRepository
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from src.infrastructure.cache.repository import MultiLayerCacheRepository
from src.infrastructure.llm.client import LLMClient
from src.infrastructure.llm.generators.factory import QueryGeneratorFactory
from src.application.services.discovery_service import DiscoveryService
from src.application.services.query_service import QueryService
from src.application.services.visualization_service import VisualizationService

from src.api.routes import discovery, query, visualization, indexing, stats, history, health, management, templates, export, optimization, batch, scheduler, metrics, websocket, pagination, transformation, analytics, auth, versioning, api_keys, comparison, chart_templates, dashboards, sharing, cache, cost_tracking, webhooks, compression, pool_management, export_templates, scheduled_exports
from src.infrastructure.vector_db.content_indexer import ContentIndexer
from src.application.services.indexing_service import IndexingService
from src.api.middleware.error_handler import (
    discoverer_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from src.core.exceptions import DiscovererException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    """Application factory - DRY: Reusable setup."""
    settings = get_settings()
    
    app = FastAPI(
        title="The Discoverer",
        description="AI-powered database discovery and query agent",
        version="1.0.0"
    )
    
    # Request ID middleware (first, so all requests have IDs)
    app.add_middleware(RequestIDMiddleware)
    
    # Logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Error handlers
    app.add_exception_handler(DiscovererException, discoverer_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Store debug mode
    app.state.debug = settings.debug
    
    # Initialize dependencies
    db_repository = InMemoryDatabaseRepository()
    vector_db_client = QdrantVectorDBClient()
    embedding_generator = EmbeddingGenerator()
    schema_indexer = SchemaIndexer(vector_db_client, embedding_generator)
    vector_db_repository = VectorDBRepository(vector_db_client, embedding_generator)
    cache = MultiLayerCacheRepository()
    llm_client = LLMClient()
    query_generator_factory = QueryGeneratorFactory(llm_client)
    
    # Initialize services
    discovery_service = DiscoveryService(db_repository, schema_indexer, cache)
    query_history_repository = QueryHistoryRepository(max_history=1000)
    
    query_service = QueryService(
        db_repository,
        vector_db_repository,
        query_generator_factory,
        cache,
        query_history_repository
    )
    visualization_service = VisualizationService()
    content_indexer = ContentIndexer(vector_db_client, embedding_generator)
    indexing_service = IndexingService(content_indexer, db_repository)
    health_monitor = DatabaseHealthMonitor(db_repository, check_interval=30)
    
    # Query templates
    template_repository = QueryTemplateRepository()
    template_service = QueryTemplateService(template_repository, query_service)
    
    # Batch query service
    batch_service = BatchQueryService(query_service)
    
    # Scheduler service
    scheduler_repository = ScheduledQueryRepository()
    scheduler_service = SchedulerService(scheduler_repository, query_service)
    
    # User repository
    user_repository = UserRepository()
    
    # Store in app state
    app.state.db_repository = db_repository
    app.state.vector_db_client = vector_db_client
    app.state.discovery_service = discovery_service
    app.state.query_service = query_service
    app.state.visualization_service = visualization_service
    app.state.indexing_service = indexing_service
    app.state.query_history_repository = query_history_repository
    app.state.health_monitor = health_monitor
    app.state.template_service = template_service
    app.state.batch_service = batch_service
    app.state.scheduler_service = scheduler_service
    app.state.user_repository = user_repository
    
    # Register routes
    app.include_router(discovery.router)
    app.include_router(query.router)
    app.include_router(visualization.router)
    app.include_router(indexing.router)
    app.include_router(stats.router)
    app.include_router(history.router)
    app.include_router(health.router)
    app.include_router(management.router)
    app.include_router(templates.router)
    app.include_router(export.router)
    app.include_router(optimization.router)
    app.include_router(batch.router)
    app.include_router(scheduler.router)
    app.include_router(metrics.router)
    app.include_router(websocket.router)
    app.include_router(pagination.router)
    app.include_router(transformation.router)
    app.include_router(analytics.router)
    app.include_router(auth.router)
    app.include_router(versioning.router)
    app.include_router(api_keys.router)
    app.include_router(comparison.router)
    app.include_router(chart_templates.router)
    app.include_router(dashboards.router)
    app.include_router(sharing.router)
    app.include_router(cache.router)
    app.include_router(cost_tracking.router)
    app.include_router(webhooks.router)
    app.include_router(compression.router)
    app.include_router(pool_management.router)
    app.include_router(export_templates.router)
    app.include_router(scheduled_exports.router)
    
    @app.on_event("startup")
    async def startup():
        """Initialize on startup."""
        # Initialize vector DB collections
        await vector_db_client.initialize_collections()
        
        # Start database health monitoring (already initialized)
        if hasattr(app.state, 'health_monitor'):
            await app.state.health_monitor.start_monitoring()
        
        # Start scheduler
        await scheduler_service.start_scheduler(check_interval=60)
        
        # Start scheduled export scheduler
        if hasattr(app.state, 'scheduled_export_service'):
            await app.state.scheduled_export_service.start_scheduler(check_interval=60)
    
    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup on shutdown."""
        # Stop health monitoring
        await health_monitor.stop_monitoring()
        
        # Stop scheduler
        await scheduler_service.stop_scheduler()
        
        # Stop scheduled export scheduler
        if hasattr(app.state, 'scheduled_export_service'):
            await app.state.scheduled_export_service.stop_scheduler()
        
        # Close all connection pools
        if hasattr(app.state, 'pool_manager'):
            await app.state.pool_manager.close_all_pools()
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "The Discoverer",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint with system status."""
        health_status = {
            "status": "healthy",
            "services": {}
        }
        
        # Check vector DB
        try:
            await vector_db_client.initialize_collections()
            health_status["services"]["vector_db"] = "healthy"
        except Exception as e:
            health_status["services"]["vector_db"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check cache
        try:
            await cache.get("health_check")
            health_status["services"]["cache"] = "healthy"
        except Exception as e:
            health_status["services"]["cache"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
    
    return app


app = create_app()


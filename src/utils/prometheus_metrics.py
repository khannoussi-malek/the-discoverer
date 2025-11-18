"""Prometheus metrics collection."""
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time


# Query metrics
query_counter = Counter(
    'discoverer_queries_total',
    'Total number of queries executed',
    ['database_type', 'status']
)

query_duration = Histogram(
    'discoverer_query_duration_seconds',
    'Query execution duration in seconds',
    ['database_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

query_cache_hits = Counter(
    'discoverer_cache_hits_total',
    'Total number of cache hits',
    ['cache_layer']
)

query_cache_misses = Counter(
    'discoverer_cache_misses_total',
    'Total number of cache misses',
    ['cache_layer']
)

# Database metrics
database_connections = Gauge(
    'discoverer_database_connections',
    'Number of active database connections',
    ['database_id', 'database_type']
)

database_health = Gauge(
    'discoverer_database_health',
    'Database health status (1=healthy, 0=unhealthy)',
    ['database_id', 'database_type']
)

# Vector DB metrics
vector_db_operations = Counter(
    'discoverer_vector_db_operations_total',
    'Total number of vector DB operations',
    ['operation_type', 'status']
)

vector_db_duration = Histogram(
    'discoverer_vector_db_duration_seconds',
    'Vector DB operation duration in seconds',
    ['operation_type']
)

# LLM metrics
llm_requests = Counter(
    'discoverer_llm_requests_total',
    'Total number of LLM requests',
    ['model', 'status']
)

llm_duration = Histogram(
    'discoverer_llm_duration_seconds',
    'LLM request duration in seconds',
    ['model']
)

llm_tokens = Counter(
    'discoverer_llm_tokens_total',
    'Total number of LLM tokens used',
    ['model', 'type']  # type: prompt or completion
)

# System metrics
active_queries = Gauge(
    'discoverer_active_queries',
    'Number of currently active queries'
)

scheduled_queries = Gauge(
    'discoverer_scheduled_queries',
    'Number of scheduled queries',
    ['status']
)


class MetricsCollector:
    """Metrics collection helper."""
    
    @staticmethod
    def record_query(
        database_type: str,
        duration: float,
        status: str = "success",
        cached: bool = False
    ):
        """Record query metrics."""
        query_counter.labels(database_type=database_type, status=status).inc()
        query_duration.labels(database_type=database_type).observe(duration)
        
        if cached:
            query_cache_hits.labels(cache_layer="multi").inc()
        else:
            query_cache_misses.labels(cache_layer="multi").inc()
    
    @staticmethod
    def record_vector_db_operation(
        operation_type: str,
        duration: float,
        status: str = "success"
    ):
        """Record vector DB operation metrics."""
        vector_db_operations.labels(
            operation_type=operation_type,
            status=status
        ).inc()
        vector_db_duration.labels(operation_type=operation_type).observe(duration)
    
    @staticmethod
    def record_llm_request(
        model: str,
        duration: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        status: str = "success"
    ):
        """Record LLM request metrics."""
        llm_requests.labels(model=model, status=status).inc()
        llm_duration.labels(model=model).observe(duration)
        
        if prompt_tokens > 0:
            llm_tokens.labels(model=model, type="prompt").inc(prompt_tokens)
        if completion_tokens > 0:
            llm_tokens.labels(model=model, type="completion").inc(completion_tokens)
    
    @staticmethod
    def update_database_health(
        database_id: str,
        database_type: str,
        healthy: bool
    ):
        """Update database health metric."""
        database_health.labels(
            database_id=database_id,
            database_type=database_type
        ).set(1 if healthy else 0)
    
    @staticmethod
    def update_active_queries(count: int):
        """Update active queries count."""
        active_queries.set(count)
    
    @staticmethod
    def update_scheduled_queries(status: str, count: int):
        """Update scheduled queries count."""
        scheduled_queries.labels(status=status).set(count)
    
    @staticmethod
    def get_metrics() -> bytes:
        """Get Prometheus metrics in text format."""
        return generate_latest()



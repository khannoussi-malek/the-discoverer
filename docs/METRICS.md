# Prometheus Metrics Documentation

## Overview

Navo exposes Prometheus-compatible metrics for monitoring and observability. All metrics are available at `/api/metrics/prometheus`.

## Metrics Endpoint

```bash
GET /api/metrics/prometheus
```

Returns metrics in Prometheus text format.

## Available Metrics

### Query Metrics

#### `discoverer_queries_total`
Total number of queries executed.

**Labels:**
- `database_type` - Type of database (postgresql, mongodb, etc.)
- `status` - Query status (success, error)

**Example:**
```
discoverer_queries_total{database_type="postgresql",status="success"} 150
discoverer_queries_total{database_type="mongodb",status="error"} 5
```

#### `discoverer_query_duration_seconds`
Query execution duration histogram.

**Labels:**
- `database_type` - Type of database

**Buckets:** 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0 seconds

**Example:**
```
discoverer_query_duration_seconds_bucket{database_type="postgresql",le="1.0"} 120
discoverer_query_duration_seconds_sum{database_type="postgresql"} 85.5
discoverer_query_duration_seconds_count{database_type="postgresql"} 150
```

#### `discoverer_cache_hits_total`
Total number of cache hits.

**Labels:**
- `cache_layer` - Cache layer (multi, in_memory, redis)

#### `discoverer_cache_misses_total`
Total number of cache misses.

**Labels:**
- `cache_layer` - Cache layer

### Database Metrics

#### `discoverer_database_connections`
Number of active database connections.

**Labels:**
- `database_id` - Database identifier
- `database_type` - Type of database

#### `discoverer_database_health`
Database health status (1=healthy, 0=unhealthy).

**Labels:**
- `database_id` - Database identifier
- `database_type` - Type of database

### Vector DB Metrics

#### `discoverer_vector_db_operations_total`
Total number of vector DB operations.

**Labels:**
- `operation_type` - Operation type (search, upsert, delete)
- `status` - Operation status (success, error)

#### `discoverer_vector_db_duration_seconds`
Vector DB operation duration histogram.

**Labels:**
- `operation_type` - Operation type

### LLM Metrics

#### `discoverer_llm_requests_total`
Total number of LLM requests.

**Labels:**
- `model` - LLM model name (gpt-3.5-turbo, gpt-4, etc.)
- `status` - Request status (success, error)

#### `discoverer_llm_duration_seconds`
LLM request duration histogram.

**Labels:**
- `model` - LLM model name

#### `discoverer_llm_tokens_total`
Total number of LLM tokens used.

**Labels:**
- `model` - LLM model name
- `type` - Token type (prompt, completion)

### System Metrics

#### `discoverer_active_queries`
Number of currently active queries (gauge).

#### `discoverer_scheduled_queries`
Number of scheduled queries.

**Labels:**
- `status` - Schedule status (active, paused)

## Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'discoverer'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/metrics/prometheus'
```

## Grafana Dashboard

You can create Grafana dashboards using these metrics:

1. **Query Performance Dashboard**
   - Query rate over time
   - Query duration percentiles
   - Error rate
   - Cache hit ratio

2. **Database Health Dashboard**
   - Database connection count
   - Database health status
   - Per-database query metrics

3. **LLM Usage Dashboard**
   - LLM request rate
   - Token usage
   - Cost estimation (if token costs are known)
   - Model distribution

4. **System Overview Dashboard**
   - Active queries
   - Scheduled queries
   - Vector DB operations
   - Overall system health

## Example Queries

### Query Rate
```
rate(discoverer_queries_total[5m])
```

### Average Query Duration
```
rate(discoverer_query_duration_seconds_sum[5m]) / rate(discoverer_query_duration_seconds_count[5m])
```

### Cache Hit Ratio
```
rate(discoverer_cache_hits_total[5m]) / (rate(discoverer_cache_hits_total[5m]) + rate(discoverer_cache_misses_total[5m]))
```

### Error Rate
```
rate(discoverer_queries_total{status="error"}[5m]) / rate(discoverer_queries_total[5m])
```

### LLM Token Usage Rate
```
rate(discoverer_llm_tokens_total[5m])
```

## Best Practices

1. **Monitor Key Metrics**: Set up alerts for error rates, slow queries, and database health
2. **Track Costs**: Monitor LLM token usage for cost management
3. **Performance Baselines**: Establish baseline metrics for normal operation
4. **Dashboard Creation**: Create dashboards for different stakeholders (ops, dev, business)
5. **Alerting**: Set up alerts for:
   - High error rates
   - Slow queries (>5s)
   - Database health issues
   - High LLM token usage

## Integration

The metrics are automatically collected during normal operation. No additional configuration is needed beyond accessing the metrics endpoint.



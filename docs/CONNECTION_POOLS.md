# Connection Pool Management Documentation

## Overview

Navo provides per-database connection pool management, allowing fine-grained control over database connections for optimal performance and resource utilization.

## Features

- **Per-Database Pools**: Independent connection pools for each database
- **Configurable Pool Sizes**: Set min/max pool sizes per database
- **Pool Statistics**: Monitor pool usage and performance
- **Health Checks**: Verify pool health and connectivity
- **Lifecycle Management**: Initialize, refresh, and close pools
- **Automatic Cleanup**: Pools closed on application shutdown

## Pool Configuration

### Default Configuration

```python
PoolConfig(
    min_size=2,              # Minimum connections in pool
    max_size=10,             # Maximum connections in pool
    max_queries=50000,       # Max queries per connection
    max_inactive_time=300.0, # Seconds before idle connection timeout
    timeout=30.0             # Connection timeout in seconds
)
```

### Database-Specific Configuration

Configure pools per database in database config:

```json
{
  "id": "db-1",
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "config": {
    "pool": {
      "min_size": 5,
      "max_size": 20,
      "max_queries": 100000,
      "max_inactive_time": 600.0,
      "timeout": 60.0
    }
  }
}
```

## API Endpoints

### List All Pools

```http
GET /api/pools
```

**Response:**
```json
{
  "pools": [
    {
      "database_id": "db-1",
      "status": "active",
      "min_size": 2,
      "max_size": 10,
      "current_size": 5,
      "active_connections": 3,
      "idle_connections": 2,
      "total_queries": 1500,
      "failed_queries": 2,
      "last_used": "2024-01-01T12:00:00",
      "uptime_seconds": 3600
    }
  ],
  "total": 1
}
```

### Get Pool Information

```http
GET /api/pools/{database_id}
```

**Response:**
```json
{
  "database_id": "db-1",
  "status": "active",
  "config": {
    "min_size": 2,
    "max_size": 10,
    "max_queries": 50000,
    "max_inactive_time": 300.0,
    "timeout": 30.0
  },
  "stats": {
    "current_size": 5,
    "active_connections": 3,
    "idle_connections": 2,
    "total_queries": 1500,
    "failed_queries": 2,
    "created_at": "2024-01-01T11:00:00",
    "last_used": "2024-01-01T12:00:00",
    "uptime_seconds": 3600
  }
}
```

### Pool Health Check

```http
GET /api/pools/{database_id}/health
```

**Response:**
```json
{
  "healthy": true,
  "status": "active",
  "connected": true,
  "stats": {
    "current_size": 5,
    "active_connections": 3,
    "idle_connections": 2
  }
}
```

### Initialize Pool

```http
POST /api/pools/{database_id}/initialize
Content-Type: application/json

{
  "min_size": 5,
  "max_size": 20,
  "max_queries": 100000,
  "max_inactive_time": 600.0,
  "timeout": 60.0
}
```

**Response:**
```json
{
  "message": "Pool initialized successfully",
  "database_id": "db-1",
  "connected": true
}
```

### Update Pool Configuration

```http
POST /api/pools/{database_id}/config
Content-Type: application/json

{
  "min_size": 5,
  "max_size": 20,
  "max_queries": 100000,
  "max_inactive_time": 600.0,
  "timeout": 60.0
}
```

**Response:**
```json
{
  "message": "Pool configuration updated",
  "config": {
    "min_size": 5,
    "max_size": 20,
    "max_queries": 100000,
    "max_inactive_time": 600.0,
    "timeout": 60.0
  }
}
```

### Refresh Pool

```http
POST /api/pools/{database_id}/refresh
```

**Response:**
```json
{
  "message": "Pool refreshed successfully"
}
```

### Close Pool

```http
DELETE /api/pools/{database_id}
```

**Response:**
```json
{
  "message": "Pool closed successfully"
}
```

## Pool Status

Pools can have the following statuses:

- **active**: Pool is active and ready for connections
- **idle**: Pool is idle (no active connections)
- **error**: Pool encountered an error
- **closed**: Pool is closed

## Usage Examples

### Python SDK

```python
from src.sdk.sync_client import DiscovererClient

client = DiscovererClient("http://localhost:8000")

# Initialize pool for a database
response = client.post(
    "/api/pools/db-1/initialize",
    json={
        "min_size": 5,
        "max_size": 20
    }
)

# Get pool statistics
stats = client.get("/api/pools/db-1")
print(f"Active connections: {stats['stats']['active_connections']}")

# Health check
health = client.get("/api/pools/db-1/health")
print(f"Pool healthy: {health['healthy']}")
```

### JavaScript SDK

```javascript
const client = new DiscovererClient('http://localhost:8000');

// Initialize pool
await client.post('/api/pools/db-1/initialize', {
  min_size: 5,
  max_size: 20
});

// Get pool statistics
const stats = await client.get('/api/pools/db-1');
console.log(`Active connections: ${stats.stats.active_connections}`);

// Health check
const health = await client.get('/api/pools/db-1/health');
console.log(`Pool healthy: ${health.healthy}`);
```

## Best Practices

1. **Size Pools Appropriately**: 
   - Small applications: min=2, max=10
   - Medium applications: min=5, max=20
   - Large applications: min=10, max=50+

2. **Monitor Pool Usage**: Regularly check pool statistics to optimize sizes

3. **Set Timeouts**: Configure appropriate timeouts based on query complexity

4. **Refresh Pools**: Periodically refresh pools to clear stale connections

5. **Health Checks**: Monitor pool health in production

6. **Database-Specific Configs**: Configure pools based on database workload

## Performance Considerations

- **Connection Overhead**: Each connection consumes resources
- **Pool Size**: Too small = connection waits, too large = resource waste
- **Idle Connections**: Idle connections consume memory but reduce connection time
- **Query Distribution**: Distribute queries across connections for better performance

## Integration with Query Service

Pools are automatically used by the query service:

```python
# Query service automatically uses pool manager
result = await query_service.execute_query(
    user_query="Show me all users",
    database_ids=["db-1"]  # Uses pool for db-1
)
```

## Troubleshooting

### Pool Not Initialized

If you get "Pool not found" errors:

```http
POST /api/pools/{database_id}/initialize
```

### Pool Connection Errors

Check pool health:

```http
GET /api/pools/{database_id}/health
```

If unhealthy, refresh the pool:

```http
POST /api/pools/{database_id}/refresh
```

### High Connection Count

If active connections are at max_size:

1. Increase max_size in pool config
2. Optimize queries to reduce connection time
3. Check for connection leaks

### Stale Connections

Refresh pool to clear stale connections:

```http
POST /api/pools/{database_id}/refresh
```




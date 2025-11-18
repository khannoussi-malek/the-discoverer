# Usage Examples

## Database Discovery

### Register a PostgreSQL Database

```python
import requests

config = {
    "id": "production_db",
    "type": "postgresql",
    "name": "Production Database",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "password": "password",
    "metadata": {
        "description": "Main production database",
        "tags": ["production", "postgresql"]
    }
}

response = requests.post(
    "http://localhost:8000/api/discovery/databases",
    json=config
)
print(response.json())
```

### Register a MongoDB Database

```python
config = {
    "id": "analytics_db",
    "type": "mongodb",
    "name": "Analytics Database",
    "host": "localhost",
    "port": 27017,
    "database": "analytics",
    "user": "admin",
    "password": "password"
}

response = requests.post(
    "http://localhost:8000/api/discovery/databases",
    json=config
)
```

## Query Execution

### Simple Query

```python
query = {
    "query": "Show me all customers"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()
print(f"Found {result['total_rows']} rows")
print(f"Execution time: {result['execution_time']}s")
```

### Query Specific Databases

```python
query = {
    "query": "What are the top selling products?",
    "database_ids": ["production_db", "analytics_db"]
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)
```

### Complex Query

```python
query = {
    "query": "Show me customers who placed orders in the last month with total value over $1000"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)
```

## Content Indexing

### Index Table Content

```python
response = requests.post(
    "http://localhost:8000/api/indexing/databases/production_db/tables/customers/index",
    params={"strategy": "smart"}
)

print(response.json())
```

### Index with Different Strategies

```python
# Full indexing (for small tables)
requests.post(
    ".../index",
    params={"strategy": "full"}
)

# Sampled indexing (for medium tables)
requests.post(
    ".../index",
    params={"strategy": "sampled"}
)

# Aggregated indexing (for large tables)
requests.post(
    ".../index",
    params={"strategy": "aggregated"}
)
```

## Visualization

### Generate Bar Chart

```python
# First execute a query
query_response = requests.post(
    "http://localhost:8000/api/query/execute",
    json={"query": "Show sales by category"}
)

query_id = query_response.json()["query_id"]

# Then generate visualization
viz_request = {
    "query_id": query_id,
    "chart_type": "bar",
    "x_axis": "category",
    "y_axis": "sales",
    "title": "Sales by Category"
}

response = requests.post(
    "http://localhost:8000/api/visualization/generate",
    json=viz_request
)
```

## Performance Monitoring

### Get Performance Statistics

```python
response = requests.get(
    "http://localhost:8000/api/stats/performance"
)

stats = response.json()
print(f"Total operations: {stats['summary']['total_operations']}")
print(f"Operations tracked: {stats['summary']['operations_tracked']}")

# View specific metrics
for operation, metrics in stats['metrics'].items():
    print(f"{operation}: avg={metrics['avg']:.3f}s, p95={metrics['p95']:.3f}s")
```

## Health Checks

### Check System Health

```python
response = requests.get("http://localhost:8000/health")
health = response.json()

print(f"Status: {health['status']}")
for service, status in health['services'].items():
    print(f"{service}: {status}")
```

## Error Handling

### Handle Errors

```python
try:
    response = requests.post(
        "http://localhost:8000/api/discovery/databases",
        json=invalid_config
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"Error: {error['error']}")
    print(f"Message: {error['message']}")
    print(f"Detail: {error.get('detail', {})}")
```

## Python Client Example

```python
from src.api.main import app
from src.application.services.discovery_service import DiscoveryService
from src.application.services.query_service import QueryService

# Initialize services (normally done via dependency injection)
# ...

# Discover database
config = {
    "id": "my_db",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb"
}

database = await discovery_service.discover_database(config)

# Execute query
result = await query_service.execute_query("Show me all users")

print(f"Found {result.total_rows} rows")
print(f"Execution time: {result.execution_time}s")
```


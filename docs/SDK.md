# Python SDK Documentation

> 📖 **Navigation**: [Documentation Index](README.md) | [Getting Started](GETTING_STARTED.md) | [Examples](EXAMPLES.md) | [API Reference](API.md) | [JavaScript SDK](JAVASCRIPT_SDK.md)

## Installation

```bash
pip install -e .
```

Or install from requirements:

```bash
pip install httpx
```

## Quick Start

### Async Client

```python
import asyncio
from src.sdk.client import DiscovererClient, DiscovererConfig

async def main():
    config = DiscovererConfig(
        base_url="http://localhost:8000",
        api_key="your-token-here"  # Optional
    )
    
    async with DiscovererClient(config) as client:
        # Register a database
        db = await client.register_database({
            "id": "db1",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "postgres",
            "password": "password"
        })
        print(f"Registered: {db}")
        
        # Execute a query
        result = await client.execute_query("Count all users")
        print(f"Result: {result['total_rows']} rows")
        
        # Generate a chart
        chart = await client.generate_chart(
            query_id=result['query_id'],
            chart_type="bar",
            x_axis="category",
            y_axis="value"
        )
        print(f"Chart generated: {chart['chart_type']}")

asyncio.run(main())
```

### Sync Client

```python
from src.sdk.sync_client import DiscovererSyncClient, DiscovererConfig

config = DiscovererConfig(base_url="http://localhost:8000")

with DiscovererSyncClient(config) as client:
    # List databases
    databases = client.list_databases()
    print(f"Found {len(databases)} databases")
    
    # Execute query
    result = client.execute_query(
        "Show top 10 products by sales",
        database_ids=["db1"],
        page=1,
        page_size=10
    )
    
    # Export result
    csv_data = client.export_query(result['query_id'], format="csv")
    with open("result.csv", "wb") as f:
        f.write(csv_data)
```

## API Reference

### DiscovererClient (Async)

#### Discovery
- `register_database(config: Dict) -> Dict` - Register a database
- `list_databases() -> List[Dict]` - List all databases
- `get_database(database_id: str) -> Dict` - Get database details
- `sync_database(database_id: str) -> Dict` - Sync database schema

#### Query
- `execute_query(query: str, database_ids: Optional[List[str]] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict` - Execute query
- `analyze_query(query: str) -> Dict` - Analyze query without executing

#### Visualization
- `generate_chart(query_id: str, chart_type: str, x_axis: Optional[str] = None, y_axis: Optional[str] = None, title: Optional[str] = None) -> Dict` - Generate chart

#### Templates
- `create_template(name: str, query: str, database_ids: Optional[List[str]] = None, description: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict` - Create template
- `list_templates(page: int = 1, page_size: int = 20, tags: Optional[List[str]] = None) -> Dict` - List templates
- `execute_template(template_id: str, parameters: Optional[Dict] = None) -> Dict` - Execute template

#### Export
- `export_query(query_id: str, format: str = "csv") -> bytes` - Export query result

#### Analytics
- `get_analytics(days: int = 7) -> Dict` - Get usage analytics
- `get_top_queries(limit: int = 10, days: int = 7) -> Dict` - Get top queries

#### Health
- `health_check() -> Dict` - Check API health

### DiscovererSyncClient (Sync)

Same methods as async client, but synchronous.

## Examples

### Complete Workflow

```python
from src.sdk.sync_client import DiscovererSyncClient, DiscovererConfig

config = DiscovererConfig(base_url="http://localhost:8000")

with DiscovererSyncClient(config) as client:
    # 1. Register database
    db = client.register_database({
        "id": "analytics_db",
        "type": "postgresql",
        "host": "db.example.com",
        "port": 5432,
        "database": "analytics",
        "user": "analyst",
        "password": "secret"
    })
    
    # 2. Sync schema
    client.sync_database("analytics_db")
    
    # 3. Execute query
    result = client.execute_query(
        "Show monthly revenue trends",
        database_ids=["analytics_db"]
    )
    
    # 4. Generate visualization
    chart = client.generate_chart(
        query_id=result['query_id'],
        chart_type="line",
        x_axis="month",
        y_axis="revenue",
        title="Monthly Revenue Trends"
    )
    
    # 5. Export data
    csv_data = client.export_query(result['query_id'], format="csv")
    with open("revenue_report.csv", "wb") as f:
        f.write(csv_data)
```

### Using Templates

```python
# Create template
template = client.create_template(
    name="Daily Sales Report",
    query="SELECT date, SUM(amount) as total FROM sales WHERE date >= '{{start_date}}' GROUP BY date",
    database_ids=["analytics_db"],
    tags=["sales", "daily"]
)

# Execute with parameters
result = client.execute_template(
    template_id=template['id'],
    parameters={"start_date": "2024-01-01"}
)
```

### Error Handling

```python
from httpx import HTTPStatusError

try:
    result = client.execute_query("Invalid query")
except HTTPStatusError as e:
    print(f"Error {e.response.status_code}: {e.response.text}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Authentication

Set API key in config:

```python
config = DiscovererConfig(
    base_url="https://api.example.com",
    api_key="your-jwt-token"
)
```

The SDK will automatically include the token in all requests.

## Best Practices

1. **Use Context Managers**: Always use `async with` or `with` for proper cleanup
2. **Error Handling**: Wrap calls in try/except for HTTP errors
3. **Connection Pooling**: Reuse client instances when possible
4. **Timeouts**: Set appropriate timeouts for long-running queries
5. **Pagination**: Use pagination for large result sets



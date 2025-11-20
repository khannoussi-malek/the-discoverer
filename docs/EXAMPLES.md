# Usage Examples

> 📖 **Navigation**: [Documentation Index](README.md) | [Getting Started](GETTING_STARTED.md) | [API Reference](API.md) | [Python SDK](SDK.md) | [JavaScript SDK](JAVASCRIPT_SDK.md)

This guide provides practical, real-world examples of using Navo. Each example includes:
- **What it does** - Clear explanation
- **When to use it** - Use case scenarios
- **Code example** - Ready-to-use code
- **Expected output** - What you'll get

## Table of Contents

1. [Database Registration Examples](#database-registration-examples)
2. [Query Execution Examples](#query-execution-examples)
3. [Visualization Examples](#visualization-examples)
4. [Python SDK Examples](#python-sdk-examples)
5. [JavaScript SDK Examples](#javascript-sdk-examples)
6. [Advanced Use Cases](#advanced-use-cases)

---

## Database Registration Examples

### Example 1: Register a PostgreSQL Database

**What it does:** Registers a PostgreSQL database so Navo can query it.

**When to use:** When you have a PostgreSQL database you want to query.

**Code:**
```python
import requests

# Database configuration
config = {
    "id": "production_db",
    "type": "postgresql",
    "name": "Production Database",
    "host": "db.example.com",
    "port": 5432,
    "database": "ecommerce",
    "user": "readonly_user",
    "password": "secure_password",
    "metadata": {
        "description": "Main production e-commerce database",
        "tags": ["production", "postgresql", "ecommerce"]
    }
}

# Register the database
response = requests.post(
    "http://localhost:8000/api/discovery/databases",
    json=config
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Database registered: {result['id']}")
    print(f"   Status: {result['status']}")
    print(f"   Schema extracted: {result.get('schema_extracted', False)}")
else:
    print(f"❌ Error: {response.json()}")
```

**Expected Output:**
```json
{
  "id": "production_db",
  "name": "Production Database",
  "type": "postgresql",
  "status": "connected",
  "schema_extracted": true,
  "tables_count": 25,
  "columns_count": 180
}
```

**What happens automatically:**
1. Navo connects to your database
2. Extracts all tables, columns, and relationships
3. Indexes the schema into the vector database
4. Makes it searchable via natural language

---

### Example 2: Register a MongoDB Database

**What it does:** Registers a MongoDB database for NoSQL querying.

**When to use:** When you have a MongoDB database with document collections.

**Code:**
```python
config = {
    "id": "analytics_db",
    "type": "mongodb",
    "name": "Analytics Database",
    "host": "mongo.example.com",
    "port": 27017,
    "database": "analytics",
    "user": "analytics_user",
    "password": "password",
    "metadata": {
        "description": "Analytics and event tracking data",
        "tags": ["analytics", "mongodb", "events"]
    }
}

response = requests.post(
    "http://localhost:8000/api/discovery/databases",
    json=config
)

print(response.json())
```

**Expected Output:**
```json
{
  "id": "analytics_db",
  "name": "Analytics Database",
  "type": "mongodb",
  "status": "connected",
  "schema_extracted": true,
  "collections_count": 12
}
```

---

### Example 3: Register Multiple Databases

**What it does:** Registers multiple databases at once using a configuration file.

**When to use:** When you have multiple databases to register.

**Step 1: Create `databases.yaml`**
```yaml
databases:
  - id: production_db
    type: postgresql
    name: Production Database
    host: ${PROD_DB_HOST}
    port: 5432
    database: ${PROD_DB_NAME}
    user: ${PROD_DB_USER}
    password: ${PROD_DB_PASSWORD}

  - id: staging_db
    type: postgresql
    name: Staging Database
    host: ${STAGING_DB_HOST}
    port: 5432
    database: ${STAGING_DB_NAME}
    user: ${STAGING_DB_USER}
    password: ${STAGING_DB_PASSWORD}
```

**Step 2: Load databases**
```bash
python scripts/load_databases.py config/databases.yaml
```

---

## Query Execution Examples

### Example 1: Simple Query - List All Records

**What it does:** Executes a simple query to retrieve all records from a table.

**When to use:** When you want to see all data in a table.

**Code:**
```python
query = {
    "query": "Show me all customers"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()

print(f"Query ID: {result['query_id']}")
print(f"Total rows: {result['total_rows']}")
print(f"Execution time: {result['execution_time']:.3f}s")
print(f"\nFirst 5 rows:")
for row in result['data'][:5]:
    print(row)
```

**Expected Output:**
```
Query ID: abc123def456
Total rows: 150
Execution time: 0.234s

First 5 rows:
{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'created_at': '2024-01-15'}
{'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'created_at': '2024-01-16'}
{'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'created_at': '2024-01-17'}
{'id': 4, 'name': 'Alice Brown', 'email': 'alice@example.com', 'created_at': '2024-01-18'}
{'id': 5, 'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'created_at': '2024-01-19'}
```

---

### Example 2: Aggregation Query - Count and Sum

**What it does:** Performs aggregation operations like counting or summing.

**When to use:** When you need statistics or summaries.

**Code:**
```python
# Count records
query = {
    "query": "How many orders were placed in the last month?"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()
print(f"Total orders: {result['data'][0]['count']}")

# Sum query
query = {
    "query": "What is the total revenue for this year?"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()
print(f"Total revenue: ${result['data'][0]['total_revenue']:,.2f}")
```

**Expected Output:**
```
Total orders: 1,234
Total revenue: $125,450.50
```

---

### Example 3: Complex Query - Multiple Conditions

**What it does:** Executes queries with multiple filters and conditions.

**When to use:** When you need to filter data based on multiple criteria.

**Code:**
```python
query = {
    "query": "Show me customers who placed orders in the last month with total value over $1000"
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()

print(f"Found {result['total_rows']} customers matching criteria:")
for customer in result['data']:
    print(f"  - {customer['name']}: ${customer['total_spent']:,.2f}")
```

**Expected Output:**
```
Found 45 customers matching criteria:
  - John Doe: $1,250.00
  - Jane Smith: $2,340.50
  - Bob Johnson: $1,890.25
  ...
```

---

### Example 4: Query Specific Databases

**What it does:** Targets specific databases when you have multiple registered.

**When to use:** When you want to query only certain databases.

**Code:**
```python
query = {
    "query": "What are the top selling products?",
    "database_ids": ["production_db", "analytics_db"]
}

response = requests.post(
    "http://localhost:8000/api/query/execute",
    json=query
)

result = response.json()
# Results will be aggregated from both databases
```

---

### Example 5: Analyze Query Without Executing

**What it does:** Analyzes a query to see what it would do without executing it.

**When to use:** When you want to preview a query before running it.

**Code:**
```python
query = {
    "query": "Count all orders"
}

response = requests.post(
    "http://localhost:8000/api/query/analyze",
    json=query
)

analysis = response.json()

print("Query Analysis:")
print(f"  Generated SQL: {analysis['generated_query']}")
print(f"  Target tables: {', '.join(analysis['target_tables'])}")
print(f"  Complexity: {analysis['complexity']}")
print(f"  Estimated execution time: {analysis['estimated_time']}s")
```

**Expected Output:**
```json
{
  "generated_query": "SELECT COUNT(*) FROM orders",
  "target_tables": ["orders"],
  "complexity": "simple",
  "estimated_time": 0.05,
  "database_ids": ["production_db"]
}
```

---

## Visualization Examples

### Example 1: Generate a Bar Chart

**What it does:** Creates a bar chart from query results.

**When to use:** When you want to visualize categorical data.

**Code:**
```python
# Step 1: Execute a query
query_response = requests.post(
    "http://localhost:8000/api/query/execute",
    json={"query": "Show sales by product category"}
)

query_id = query_response.json()["query_id"]

# Step 2: Generate visualization
viz_request = {
    "query_id": query_id,
    "chart_type": "bar",
    "x_axis": "category",
    "y_axis": "sales",
    "title": "Sales by Product Category"
}

viz_response = requests.post(
    "http://localhost:8000/api/visualization/generate",
    json=viz_request
)

chart = viz_response.json()
print(f"Chart created: {chart['chart_id']}")
print(f"Chart HTML: {chart['chart_html'][:100]}...")
```

**Expected Output:**
```json
{
  "chart_id": "chart_123",
  "chart_type": "bar",
  "chart_html": "<div>...</div>",
  "chart_config": {...}
}
```

---

### Example 2: Automatic Chart Type Detection

**What it does:** Lets Navo automatically choose the best chart type.

**When to use:** When you're not sure which chart type to use.

**Code:**
```python
query_response = requests.post(
    "http://localhost:8000/api/query/execute",
    json={"query": "Show sales trends over time"}
)

query_id = query_response.json()["query_id"]

# Don't specify chart_type - let it auto-detect
viz_request = {
    "query_id": query_id,
    "x_axis": "date",
    "y_axis": "sales",
    "title": "Sales Trends"
}

viz_response = requests.post(
    "http://localhost:8000/api/visualization/generate",
    json=viz_request
)

chart = viz_response.json()
print(f"Auto-selected chart type: {chart['chart_type']}")
# Will likely be "line" for time series data
```

---

### Example 3: Export Chart as Image

**What it does:** Exports a chart as PNG, PDF, or other formats.

**When to use:** When you need to save or share charts.

**Code:**
```python
# After creating a chart (from previous example)
chart_id = chart['chart_id']

# Export as PNG
export_response = requests.get(
    f"http://localhost:8000/api/visualization/charts/{chart_id}/export",
    params={"format": "png"}
)

# Save the image
with open("chart.png", "wb") as f:
    f.write(export_response.content)

print("Chart exported to chart.png")
```

---

## Python SDK Examples

### Example 1: Basic SDK Usage

**What it does:** Shows how to use the Python SDK for async operations.

**When to use:** When building Python applications.

**Code:**
```python
import asyncio
from src.sdk.client import NavoClient

async def main():
    # Initialize client
    client = NavoClient(base_url="http://localhost:8000")
    
    # Register database
    db = await client.register_database(
        id="my_db",
        type="postgresql",
        host="localhost",
        port=5432,
        database="mydb",
        user="user",
        password="password"
    )
    print(f"Database registered: {db['id']}")
    
    # Execute query
    result = await client.execute_query("Show me all customers")
    print(f"Found {result['total_rows']} customers")
    
    # Generate visualization
    chart = await client.generate_chart(
        query_id=result['query_id'],
        chart_type="bar",
        x_axis="name",
        y_axis="count"
    )
    print(f"Chart created: {chart['chart_id']}")

# Run the async function
asyncio.run(main())
```

---

### Example 2: Sync SDK Usage

**What it does:** Shows how to use the synchronous Python SDK.

**When to use:** When you prefer synchronous code or can't use async.

**Code:**
```python
from src.sdk.sync_client import DiscovererSyncClient

# Initialize sync client
client = DiscovererSyncClient(base_url="http://localhost:8000")

# Register database (synchronous)
db = client.register_database(
    id="my_db",
    type="postgresql",
    host="localhost",
    database="mydb",
    user="user",
    password="password"
)

# Execute query (synchronous)
result = client.execute_query("Show me all customers")
print(f"Found {result['total_rows']} customers")
```

---

## JavaScript SDK Examples

### Example 1: Browser Usage

**What it does:** Shows how to use the JavaScript SDK in a browser.

**When to use:** When building web applications.

**Code:**
```javascript
import { NavoClient } from 'navo-sdk';

// Initialize client
const client = new NavoClient({
  baseURL: 'http://localhost:8000'
});

// Register database
const db = await client.registerDatabase({
  id: 'my_db',
  type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'user',
  password: 'password'
});

console.log('Database registered:', db.id);

// Execute query
const result = await client.executeQuery('Show me all customers');
console.log(`Found ${result.total_rows} customers`);

// Display results in UI
result.data.forEach(customer => {
  console.log(customer);
});
```

---

### Example 2: Node.js Usage

**What it does:** Shows how to use the JavaScript SDK in Node.js.

**When to use:** When building server-side Node.js applications.

**Code:**
```javascript
const { NavoClient } = require('navo-sdk');

async function main() {
  const client = new NavoClient({
    baseURL: 'http://localhost:8000'
  });

  // Register database
  await client.registerDatabase({
    id: 'my_db',
    type: 'postgresql',
    host: 'localhost',
    database: 'mydb',
    user: 'user',
    password: 'password'
  });

  // Execute query
  const result = await client.executeQuery('Show me all customers');
  console.log(result);
}

main().catch(console.error);
```

---

## Advanced Use Cases

### Example 1: Content Indexing for Faster Queries

**What it does:** Indexes table content into the vector database for faster semantic search.

**When to use:** When you frequently query specific tables and want faster results.

**Code:**
```python
# Index a table with smart strategy (auto-selects best approach)
response = requests.post(
    "http://localhost:8000/api/indexing/databases/production_db/tables/customers/index",
    params={"strategy": "smart"}
)

result = response.json()
print(f"Indexed {result['rows_indexed']} rows")
print(f"Strategy used: {result['strategy']}")
```

**Indexing Strategies:**
- `full` - Index all rows (for small tables < 10K rows)
- `sampled` - Index a sample (for medium tables 10K-1M rows)
- `aggregated` - Index summaries (for large tables > 1M rows)
- `smart` - Automatically choose (recommended)

---

### Example 2: Create a Dashboard

**What it does:** Creates a dashboard with multiple visualizations.

**When to use:** When you want to combine multiple charts into one view.

**Code:**
```python
# Step 1: Execute multiple queries
queries = [
    {"query": "Show sales by category"},
    {"query": "Show revenue trends over time"},
    {"query": "Show top 10 customers"}
]

query_ids = []
for q in queries:
    response = requests.post(
        "http://localhost:8000/api/query/execute",
        json=q
    )
    query_ids.append(response.json()["query_id"])

# Step 2: Generate charts
chart_ids = []
for i, query_id in enumerate(query_ids):
    chart_types = ["bar", "line", "table"]
    response = requests.post(
        "http://localhost:8000/api/visualization/generate",
        json={
            "query_id": query_id,
            "chart_type": chart_types[i]
        }
    )
    chart_ids.append(response.json()["chart_id"])

# Step 3: Create dashboard
dashboard = {
    "name": "Sales Dashboard",
    "description": "Overview of sales metrics",
    "widgets": [
        {"chart_id": chart_ids[0], "position": {"x": 0, "y": 0}},
        {"chart_id": chart_ids[1], "position": {"x": 1, "y": 0}},
        {"chart_id": chart_ids[2], "position": {"x": 0, "y": 1}}
    ]
}

response = requests.post(
    "http://localhost:8000/api/dashboards",
    json=dashboard
)

dashboard_id = response.json()["dashboard_id"]
print(f"Dashboard created: {dashboard_id}")
```

---

### Example 3: Schedule Automated Queries

**What it does:** Schedules queries to run automatically on a schedule.

**When to use:** When you need regular reports or data updates.

**Code:**
```python
# Create a scheduled query (runs daily at 9 AM)
schedule = {
    "name": "Daily Sales Report",
    "query": "Show today's sales summary",
    "cron_expression": "0 9 * * *",  # 9 AM daily
    "enabled": True,
    "notifications": {
        "webhook_url": "https://your-app.com/webhook"
    }
}

response = requests.post(
    "http://localhost:8000/api/scheduler/schedules",
    json=schedule
)

schedule_id = response.json()["schedule_id"]
print(f"Scheduled query created: {schedule_id}")
```

**Cron Expression Examples:**
- `0 9 * * *` - Daily at 9 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight
- `0 0 1 * *` - First day of every month

---

### Example 4: Export Query Results

**What it does:** Exports query results to various formats.

**When to use:** When you need to share data or import into other tools.

**Code:**
```python
# Execute query
query_response = requests.post(
    "http://localhost:8000/api/query/execute",
    json={"query": "Show all customers"}
)

query_id = query_response.json()["query_id"]

# Export as CSV
csv_response = requests.get(
    f"http://localhost:8000/api/export/queries/{query_id}",
    params={"format": "csv"}
)

with open("customers.csv", "wb") as f:
    f.write(csv_response.content)

# Export as Excel
excel_response = requests.get(
    f"http://localhost:8000/api/export/queries/{query_id}",
    params={"format": "excel"}
)

with open("customers.xlsx", "wb") as f:
    f.write(excel_response.content)

print("Exports created: customers.csv, customers.xlsx")
```

---

### Example 5: Error Handling

**What it does:** Shows how to properly handle errors.

**When to use:** Always - for production code.

**Code:**
```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        "http://localhost:8000/api/discovery/databases",
        json={
            "id": "my_db",
            "type": "postgresql",
            "host": "invalid_host",
            "database": "mydb"
        },
        timeout=10
    )
    
    response.raise_for_status()
    result = response.json()
    print(f"Success: {result}")
    
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"HTTP Error {e.response.status_code}: {error.get('error', 'Unknown error')}")
    print(f"Message: {error.get('message', 'No message')}")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Next Steps

Now that you've seen practical examples:

1. **Try the examples** - Copy and modify them for your use case
2. **Explore the API** - Visit http://localhost:8000/docs for interactive docs
3. **Read SDK guides** - See [Python SDK](SDK.md) or [JavaScript SDK](JAVASCRIPT_SDK.md)
4. **Build dashboards** - Follow [Dashboards Guide](DASHBOARDS.md)
5. **Automate workflows** - Check [Scheduler Guide](SCHEDULER.md)

---

**Need more help?** Check the [Documentation Index](README.md) for complete guides.

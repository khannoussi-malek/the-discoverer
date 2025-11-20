# Getting Started Guide

> 📖 **Navigation**: [Documentation Index](README.md) | [Examples](EXAMPLES.md) | [API Reference](API.md) | [Architecture](ARCHITECTURE.md)

Welcome to Navo! This guide will help you get up and running in **5 minutes**.

## What You'll Learn

By the end of this guide, you will:
- ✅ Have Navo running on your machine
- ✅ Register your first database
- ✅ Execute your first natural language query
- ✅ Understand how to integrate it into your solution

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should show 3.10+
   ```

2. **Docker and Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```
   > **Note:** Docker is required for Redis and Qdrant (vector database) services.

3. **OpenAI API Key** (for AI-powered query generation)
   - Get one at: https://platform.openai.com/api-keys
   - You'll need this to enable natural language to SQL conversion

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/khannoussi-malek/navo.git
cd navo
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if you prefer using a virtual environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your OpenAI API key
# Open .env in your editor and set:
# OPENAI_API_KEY=your-api-key-here
```

**Required Environment Variables:**
- `OPENAI_API_KEY` - Your OpenAI API key (required for AI features)

**Optional Environment Variables:**
- `REDIS_URL` - Redis connection URL (default: `redis://localhost:6379`)
- `QDRANT_URL` - Qdrant connection URL (default: `http://localhost:6333`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Step 4: Start Required Services

Navo requires Redis (caching) and Qdrant (vector database). Start them with Docker Compose:

```bash
# Start all services (Redis, Qdrant, and optional test databases)
docker-compose up -d

# Verify services are running
docker-compose ps

# You should see:
# - qdrant (vector database)
# - redis (caching)
```

**What's happening:**
- **Qdrant**: Stores vector embeddings of your database schemas for fast semantic search
- **Redis**: Provides fast caching for query results and metadata

### Step 5: Initialize Vector Database

The vector database needs to be set up with the required collections:

```bash
# Setup vector database collections
python scripts/setup_vector_db.py
```

**Expected output:**
```
Setting up vector database...
Created collection: schemas
Created collection: content
Vector database setup complete!
```

### Step 6: Start Navo Service

```bash
# Start the FastAPI application
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or using the Makefile:
make run
```

**What you should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Step 7: Verify Installation

Open a new terminal and test the health endpoint:

```bash
# Check if the service is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","services":{"redis":"connected","qdrant":"connected"}}
```

**Or visit in your browser:**
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Your First Database Registration

Now let's register your first database. Navo needs to know about your databases before it can query them.

### Example 1: Register a PostgreSQL Database

```bash
curl -X POST "http://localhost:8000/api/discovery/databases" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_first_db",
    "type": "postgresql",
    "name": "My First Database",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "id": "my_first_db",
  "name": "My First Database",
  "type": "postgresql",
  "status": "connected",
  "schema_extracted": true
}
```

**What happens automatically:**
1. Navo connects to your database
2. Extracts the complete schema (tables, columns, relationships)
3. Indexes the schema into the vector database
4. Makes it searchable via natural language

### Example 2: Register a MySQL Database

```bash
curl -X POST "http://localhost:8000/api/discovery/databases" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "mysql_db",
    "type": "mysql",
    "name": "MySQL Database",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "root",
    "password": "password"
  }'
```

### Example 3: Register a MongoDB Database

```bash
curl -X POST "http://localhost:8000/api/discovery/databases" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "mongo_db",
    "type": "mongodb",
    "name": "MongoDB Database",
    "host": "localhost",
    "port": 27017,
    "database": "mydb",
    "user": "admin",
    "password": "password"
  }'
```

### Verify Database Registration

```bash
# List all registered databases
curl http://localhost:8000/api/discovery/databases

# Check specific database health
curl http://localhost:8000/api/health/databases/my_first_db
```

## Your First Query

Now the fun part! Let's query your database using natural language.

### Simple Query Example

```bash
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all customers"
  }'
```

**What Navo does:**
1. Understands your natural language query
2. Searches the vector database to find relevant tables/columns
3. Generates optimized SQL query using AI
4. Executes the query on your database
5. Returns results with metadata

**Response:**
```json
{
  "query_id": "abc123",
  "query": "SELECT * FROM customers",
  "total_rows": 150,
  "execution_time": 0.234,
  "data": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
  ],
  "columns": ["id", "name", "email"]
}
```

### More Complex Query Examples

```bash
# Count records
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many orders were placed last month?"}'

# Aggregation query
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me total sales by product category"}'

# Filtered query
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find all customers who spent more than $1000"}'
```

### Query Specific Databases

If you have multiple databases registered, you can target specific ones:

```bash
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all users",
    "database_ids": ["my_first_db", "mysql_db"]
  }'
```

## Using Configuration Files

Instead of registering databases one by one, you can load them from a YAML configuration file.

### Step 1: Create Configuration File

```bash
# Copy the example
cp config/databases.yaml.example config/databases.yaml
```

### Step 2: Edit Configuration

Edit `config/databases.yaml`:

```yaml
databases:
  - id: production_db
    type: postgresql
    name: Production Database
    host: ${DB_HOST}
    port: 5432
    database: ${DB_NAME}
    user: ${DB_USER}
    password: ${DB_PASSWORD}
    metadata:
      description: "Main production database"
      tags: ["production", "postgresql"]

  - id: analytics_db
    type: mongodb
    name: Analytics Database
    host: localhost
    port: 27017
    database: analytics
    user: admin
    password: password
```

### Step 3: Load Databases

```bash
# Load all databases from config
python scripts/load_databases.py config/databases.yaml

# Or use Makefile
make load-databases
```

## Common Workflows

### Workflow 1: Basic Query Workflow

1. **Register database** → Navo extracts schema automatically
2. **Wait a few seconds** → Schema indexing completes
3. **Execute queries** → Use natural language
4. **View results** → Get data + auto-generated visualizations

### Workflow 2: Content Indexing for Faster Queries

For frequently queried tables, index their content for faster semantic search:

```bash
# Index a table's content
curl -X POST "http://localhost:8000/api/indexing/databases/my_first_db/tables/customers/index?strategy=smart"
```

**Indexing Strategies:**
- `full` - Index all rows (for small tables)
- `sampled` - Index a sample of rows (for medium tables)
- `aggregated` - Index aggregated summaries (for large tables)
- `smart` - Automatically choose the best strategy

### Workflow 3: Create Visualizations

```bash
# 1. Execute a query
QUERY_RESPONSE=$(curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show sales by category"}')

# 2. Extract query_id from response
QUERY_ID=$(echo $QUERY_RESPONSE | jq -r '.query_id')

# 3. Generate visualization
curl -X POST "http://localhost:8000/api/visualization/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"query_id\": \"$QUERY_ID\",
    \"chart_type\": \"bar\",
    \"x_axis\": \"category\",
    \"y_axis\": \"sales\"
  }"
```

## Integration Options

### Option 1: Python SDK

```python
from src.sdk.client import NavoClient

# Initialize client
client = NavoClient(base_url="http://localhost:8000")

# Register database
await client.register_database(
    id="my_db",
    type="postgresql",
    host="localhost",
    database="mydb",
    user="user",
    password="password"
)

# Execute query
result = await client.execute_query("Show me all customers")
print(result.data)
```

### Option 2: JavaScript/TypeScript SDK

```javascript
import { NavoClient } from 'navo-sdk';

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
console.log(result.data);
```

### Option 3: REST API (Any Language)

```bash
# Any language that can make HTTP requests
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all customers"}'
```

## Troubleshooting

### Issue: Vector DB Connection Failed

**Symptoms:** Error about Qdrant connection

**Solution:**
```bash
# Check if Qdrant is running
docker-compose ps qdrant

# Check Qdrant logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart qdrant

# Re-run setup
python scripts/setup_vector_db.py
```

### Issue: Database Connection Failed

**Symptoms:** Database registration fails

**Solution:**
```bash
# Test database connection manually
# For PostgreSQL:
psql -h localhost -U postgres -d mydb

# Check database health
curl http://localhost:8000/api/health/databases/my_db

# Verify credentials in your request
```

### Issue: LLM Query Generation Fails

**Symptoms:** Queries return errors about OpenAI API

**Solution:**
```bash
# Verify OpenAI API key is set
echo $OPENAI_API_KEY

# Check API key in .env file
grep OPENAI_API_KEY .env

# Test API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: Service Won't Start

**Symptoms:** Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn src.api.main:app --port 8001

# Or find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Next Steps

Now that you have Navo running:

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Read Examples**: Check [Examples Guide](EXAMPLES.md) for more use cases
3. **Learn SDKs**: See [Python SDK](SDK.md) or [JavaScript SDK](JAVASCRIPT_SDK.md) guides
4. **Build Dashboards**: Follow [Dashboards Guide](DASHBOARDS.md)
5. **Deploy to Production**: See [Deployment Guide](DEPLOYMENT.md)

## Production Deployment

For production deployment, see the [Deployment Guide](DEPLOYMENT.md) which covers:
- Docker deployment
- Environment configuration
- Security best practices
- Performance tuning
- Monitoring setup

---

**Need help?** Check the [Documentation Index](README.md) or [Examples](EXAMPLES.md) for more guidance.

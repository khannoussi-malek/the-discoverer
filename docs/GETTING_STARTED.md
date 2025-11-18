# Getting Started Guide

> 📖 **Navigation**: [Documentation Index](README.md) | [Examples](EXAMPLES.md) | [API Reference](API.md) | [Architecture](ARCHITECTURE.md)

## Quick Start (5 minutes)

### 1. Prerequisites

```bash
# Install Python 3.10+
python --version

# Install Docker and Docker Compose
docker --version
docker-compose --version
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/khannoussi-malek/the-discoverer.git
cd the-discoverer

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, set OPENAI_API_KEY
```

### 3. Start Services

```bash
# Start all services (Qdrant, Redis, test databases)
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Initialize Vector Database

```bash
# Setup vector database collections
python scripts/setup_vector_db.py
```

### 5. Start Application

```bash
# Run the application
uvicorn src.api.main:app --reload

# Or use Makefile
make run
```

### 6. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs
```

## First Database Registration

### Register a PostgreSQL Database

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
    "password": "password"
  }'
```

### Verify Registration

```bash
# List all databases
curl http://localhost:8000/api/discovery/databases

# Check database health
curl http://localhost:8000/api/health/databases/my_first_db
```

## First Query

### Execute a Simple Query

```bash
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all customers"
  }'
```

### Analyze Query (without executing)

```bash
curl -X POST "http://localhost:8000/api/query/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Count all orders"
  }'
```

## Using Configuration File

### 1. Create Configuration

```bash
# Copy example
cp config/databases.yaml.example config/databases.yaml

# Edit with your database configurations
```

### 2. Load Databases

```bash
# Load all databases from config
python scripts/load_databases.py

# Or use Makefile
make load-databases
```

## Common Workflows

### Workflow 1: Discover and Query

1. Register database
2. Wait for schema extraction (automatic)
3. Execute queries
4. View results

### Workflow 2: Index Content for Fast Queries

1. Register database
2. Index table content:
   ```bash
   curl -X POST "http://localhost:8000/api/indexing/databases/my_db/tables/customers/index?strategy=smart"
   ```
3. Execute semantic queries (faster)

### Workflow 3: Monitor and Manage

1. Check database health:
   ```bash
   curl http://localhost:8000/api/health/databases
   ```
2. View query history:
   ```bash
   curl http://localhost:8000/api/history/queries?limit=10
   ```
3. Check performance stats:
   ```bash
   curl http://localhost:8000/api/stats/performance
   ```

## Troubleshooting

### Vector DB Connection Issues

```bash
# Check if Qdrant is running
docker-compose ps qdrant

# Check Qdrant logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### Database Connection Issues

```bash
# Test database connection manually
# For PostgreSQL:
psql -h localhost -U postgres -d mydb

# Check health endpoint
curl http://localhost:8000/api/health/databases/my_db
```

### LLM Issues

```bash
# Verify OpenAI API key is set
echo $OPENAI_API_KEY

# Check API key in .env file
grep OPENAI_API_KEY .env
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Read Documentation**: Check docs/ directory
3. **Try Examples**: See docs/EXAMPLES.md
4. **Customize**: Modify configuration for your needs

## Production Deployment

See [Deployment Guide](DEPLOYMENT.md) for production setup.


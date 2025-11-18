# The Discoverer

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/khannoussi-malek/the-discoverer)

AI-powered database discovery and query agent supporting multiple SQL and NoSQL databases with vector database optimization for schema and content.

## Author

**Malek Khannoussi**

- GitHub: [@khannoussi-malek](https://github.com/khannoussi-malek)
- LinkedIn: [khannoussi-malek](https://www.linkedin.com/in/khannoussi-malek/)

## Features

- **Multi-Database Support**: PostgreSQL, MySQL, MongoDB, SQLite (extensible to Cassandra, Elasticsearch)
- **Vector Database**: Fast schema and content discovery using Qdrant
- **AI-Powered Queries**: Natural language to SQL/NoSQL query generation with pattern matching
- **Performance Optimized**: 
  - Multi-layer caching (in-memory → Redis → Vector DB)
  - Parallel query execution across databases
  - Connection pooling per database
  - Batch operations for embeddings
- **Hybrid Query Routing**: Smart routing between content vector DB and schema-based queries
- **Visualization**: Automatic chart generation from query results using Plotly
- **Clean Architecture**: KISS, DRY principles with design patterns (Repository, Adapter, Factory, Strategy)

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for services)
- OpenAI API key (for LLM features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/khannoussi-malek/the-discoverer.git
cd the-discoverer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start services with Docker Compose:
```bash
docker-compose up -d
```

5. Run the application:
```bash
uvicorn src.api.main:app --reload
```

6. (Optional) Install CLI tool:
```bash
pip install -e .
# Or use directly: python -m src.cli.main
```

## CLI Usage

The Discoverer includes a command-line interface for easy interaction:

```bash
# Register a database
discoverer register --database-id db1 --type postgresql --host-db localhost --port 5432 --database mydb --user postgres --password pass

# List databases
discoverer list-databases

# Execute a query
discoverer query "Count all users" --format table

# Check health
discoverer health

# Sync database schema
discoverer sync db1

# Export query result
discoverer export query_id --format csv
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

### Database Configuration

Configure databases in `config/databases.yaml` (copy from `config/databases.yaml.example`).

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Quick Start Example

1. **Register a database:**
```bash
curl -X POST "http://localhost:8000/api/discovery/databases" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_db",
    "type": "postgresql",
    "name": "My Database",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "user",
    "password": "password"
  }'
```

2. **Execute a query:**
```bash
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all customers"
  }'
```

3. **Index table content:**
```bash
curl -X POST "http://localhost:8000/api/indexing/databases/my_db/tables/customers/index?strategy=smart"
```

## Architecture

```
src/
├── domain/          # Business entities
├── application/     # Business logic
├── infrastructure/  # External dependencies
└── api/            # Presentation layer
```

## Development

### Using Makefile

```bash
make install      # Install dependencies
make dev          # Install dev dependencies
make test         # Run tests
make lint         # Run linters
make format       # Format code
make run          # Run application
make docker-up    # Start Docker services
```

### Manual Commands

#### Running Tests

```bash
pytest
```

#### Code Quality

```bash
black src/
flake8 src/
mypy src/
```

#### Setup Vector DB

```bash
python scripts/setup_vector_db.py
```

## Features Overview

### Core Features
- ✅ Multi-database support (PostgreSQL, MySQL, SQLite, MongoDB, Cassandra, Elasticsearch)
- ✅ Vector database for fast schema/content discovery
- ✅ AI-powered query generation with pattern matching
- ✅ Hybrid query routing (content vector DB + schema-based)
- ✅ Automatic visualization generation
- ✅ Performance monitoring and statistics
- ✅ Comprehensive error handling
- ✅ Request logging
- ✅ Health checks
- ✅ Query streaming support
- ✅ Integration tests
- ✅ Query templates/saved queries
- ✅ Export functionality (CSV, JSON, Excel)
- ✅ Query result pagination
- ✅ Query optimization and analysis
- ✅ Batch query execution
- ✅ Circuit breaker for fault tolerance
- ✅ Performance benchmarking utilities
- ✅ Query scheduling (cron-like)
- ✅ Prometheus metrics
- ✅ Server-side pagination
- ✅ WebSocket support for real-time updates
- ✅ Query result transformation
- ✅ Analytics and usage tracking
- ✅ CLI Tool
- ✅ Enhanced Authentication (JWT, user management)
- ✅ Advanced visualization (10+ chart types)
- ✅ Python SDK (async and sync)
- ✅ Chart export (PNG, PDF, HTML, SVG)
- ✅ Query versioning
- ✅ Database health monitoring with automatic reconnection
- ✅ Schema change detection
- ✅ API key management and authentication
- ✅ Query result comparison
- ✅ JavaScript/TypeScript SDK
- ✅ Chart templates
- ✅ Parquet export
- ✅ Dashboard creation
- ✅ Query result sharing
- ✅ Query result caching strategies
- ✅ Cost tracking (LLM API usage)
- ✅ REST API webhooks
- ✅ Query result compression
- ✅ Database connection pooling per database
- ✅ Avro export
- ✅ Query result streaming improvements
- ✅ Export templates
- ✅ Scheduled exports

### API Endpoints
- `/api/discovery/*` - Database discovery and management
- `/api/query/*` - Query execution (with pagination and streaming)
- `/api/visualization/*` - Chart generation
- `/api/indexing/*` - Content indexing
- `/api/history/*` - Query history and statistics
- `/api/stats/*` - Performance statistics
- `/api/templates/*` - Query templates (save, list, execute, search)
- `/api/export/*` - Export query results (CSV, JSON, Excel)
- `/api/optimization/*` - Query optimization and analysis
- `/api/batch/*` - Batch query execution
- `/api/scheduler/*` - Query scheduling (create, list, execute, pause, resume)
- `/api/metrics/prometheus` - Prometheus metrics endpoint
- `/api/pagination/*` - Server-side pagination for SQL queries
- `/api/ws/*` - WebSocket endpoints for real-time updates
- `/api/transformation/*` - Query result transformation
- `/api/analytics/*` - Usage analytics and statistics
- `/api/auth/*` - Authentication (register, login, user management)
- `/api/api-keys/*` - API key management (create, list, update, revoke, delete)
- `/api/versioning/*` - Query versioning and comparison
- `/api/comparison/*` - Query result comparison
- `/api/chart-templates/*` - Chart template management
- `/api/dashboards/*` - Dashboard creation and management
- `/api/sharing/*` - Query result sharing
- `/api/cache/*` - Cache management
- `/api/cost-tracking/*` - LLM cost tracking
- `/api/webhooks/*` - Webhook management
- `/api/compression/*` - Data compression utilities
- `/api/pools/*` - Connection pool management
- `/api/export-templates/*` - Export template management
- `/api/scheduled-exports/*` - Scheduled export management
- `/health` - Health check
- `/health/databases` - Database health status
- `/health/databases/{id}` - Individual database health

### SDKs Available
- ✅ **Python SDK** - Async and sync clients (`src/sdk/client.py`, `src/sdk/sync_client.py`)
- ✅ **JavaScript/TypeScript SDK** - Browser and Node.js support (`src/sdk/javascript/`)

### Additional Features
- ✅ Query history tracking and search
- ✅ Rate limiting (60 requests/minute)
- ✅ Configuration file loading (YAML)
- ✅ SQLite database support
- ✅ Request logging middleware
- ✅ Comprehensive error handling

## Documentation

📚 **[📖 Documentation Index](docs/README.md)** - Start here! Complete navigation guide to all documentation.

### Quick Links

**Getting Started:**
- [📖 Documentation Index](docs/README.md) - Navigation hub for all docs
- [🚀 Getting Started Guide](docs/GETTING_STARTED.md) - Quick setup (5 minutes)
- [💡 Examples](docs/EXAMPLES.md) - Code samples and usage patterns

**Core Documentation:**
- [📡 API Reference](docs/API.md) - Complete API endpoint documentation
- [🏗️ Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [🚢 Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

**SDKs & Integration:**
- [🐍 Python SDK](docs/SDK.md) - Python SDK documentation (async & sync)
- [🌐 JavaScript/TypeScript SDK](docs/JAVASCRIPT_SDK.md) - Browser and Node.js support
- [⚡ CLI Tool](docs/CLI.md) - Command-line interface

**Feature Guides:**
- [📊 Dashboards](docs/DASHBOARDS.md) - Dashboard creation and management
- [📈 Chart Templates](docs/CHART_TEMPLATES.md) - Reusable chart configurations
- [🔗 Query Result Sharing](docs/QUERY_RESULT_SHARING.md) - Share query results securely
- [🔔 Webhooks](docs/WEBHOOKS.md) - Webhook configuration and usage
- [⏰ Scheduler](docs/SCHEDULER.md) - Query scheduling and automation
- [🔌 Connection Pools](docs/CONNECTION_POOLS.md) - Database connection pool management
- [🗜️ Compression](docs/COMPRESSION.md) - Data compression utilities
- [🌐 WebSocket](docs/WEBSOCKET.md) - Real-time WebSocket support
- [📊 Metrics & Monitoring](docs/METRICS.md) - Performance monitoring

**See the [Documentation Index](docs/README.md) for complete navigation and learning paths.**

## Quick Commands

```bash
# Load databases from config file
python scripts/load_databases.py config/databases.yaml

# Setup vector database
python scripts/setup_vector_db.py

# Index a database schema
python scripts/index_database.py <database_id>
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

Copyright (c) 2024 Malek Khannoussi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


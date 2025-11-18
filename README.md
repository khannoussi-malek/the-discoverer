# The Discoverer

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/khannoussi-malek/the-discoverer)

## 🎯 What is The Discoverer?

**The Discoverer** is an AI-powered database discovery and query platform that transforms how you interact with your databases. Instead of writing complex SQL queries, you simply ask questions in natural language, and The Discoverer automatically:

- **Discovers** your database schemas across multiple database types
- **Understands** your data structure using AI and vector search
- **Generates** optimized queries from natural language
- **Executes** queries across multiple databases simultaneously
- **Visualizes** results with beautiful, interactive charts
- **Shares** insights with your team through dashboards and exports

## 💡 What Problems Does It Solve?

### Problem 1: Complex Database Queries
**Before:** You need to know SQL syntax, table names, column names, and relationships to write queries.

**With The Discoverer:** Simply ask "Show me all customers who placed orders in the last month" and get results instantly.

### Problem 2: Multiple Database Types
**Before:** You need different tools and knowledge for PostgreSQL, MySQL, MongoDB, etc.

**With The Discoverer:** One platform queries all your databases using the same natural language interface.

### Problem 3: Slow Data Discovery
**Before:** You spend hours exploring schemas, understanding relationships, and finding the right tables.

**With The Discoverer:** AI-powered schema discovery with vector search finds relevant tables and columns in seconds.

### Problem 4: Manual Visualization
**Before:** Export data, import into Excel/Tableau, create charts manually.

**With The Discoverer:** Automatic chart generation from query results with 15+ chart types.

### Problem 5: Team Collaboration
**Before:** Share SQL queries via email, recreate visualizations, lose context.

**With The Discoverer:** Share query results with secure links, create dashboards, schedule automated reports.

## 🚀 What The Discoverer Offers

### Core Capabilities

1. **Natural Language Querying**
   - Ask questions in plain English: "What are the top 10 products by sales?"
   - Works across PostgreSQL, MySQL, MongoDB, SQLite, Cassandra, and Elasticsearch
   - AI automatically generates optimized SQL/NoSQL queries

2. **Intelligent Schema Discovery**
   - Automatically extracts and indexes database schemas
   - Vector-based semantic search to find relevant tables and columns
   - Understands relationships between tables

3. **Multi-Database Support**
   - Query multiple databases simultaneously
   - Unified interface for SQL and NoSQL databases
   - Smart database selection based on query intent

4. **Advanced Visualization**
   - 15+ chart types (bar, line, pie, scatter, heatmap, 3D, and more)
   - Automatic chart type detection
   - Interactive charts with Plotly
   - Export charts as PNG, PDF, HTML, or SVG

5. **Performance Optimization**
   - Multi-layer caching (in-memory → Redis → Vector DB)
   - Parallel query execution
   - Connection pooling per database
   - Query result caching strategies

6. **Enterprise Features**
   - Dashboard creation and sharing
   - Query scheduling (cron-like)
   - Webhooks for automation
   - API key management
   - JWT authentication
   - Cost tracking for LLM usage
   - Prometheus metrics

### Integration Options

- **REST API**: Full-featured REST API with OpenAPI documentation
- **Python SDK**: Async and sync clients for Python applications
- **JavaScript/TypeScript SDK**: Browser and Node.js support
- **CLI Tool**: Command-line interface for automation
- **WebSocket**: Real-time updates and streaming

## 📋 How to Implement The Discoverer in Your Solution

### Option 1: Standalone Service (Recommended)

Deploy The Discoverer as a separate microservice that your applications connect to via API or SDK.

**Best for:**
- Multiple applications needing database access
- Centralized data access layer
- Team collaboration and sharing

**Implementation Steps:**

1. **Deploy The Discoverer Service**
   ```bash
   # Clone and setup
   git clone https://github.com/khannoussi-malek/the-discoverer.git
   cd the-discoverer
   pip install -r requirements.txt
   
   # Start services (Redis, Qdrant)
   docker-compose up -d
   
   # Run the service
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Register Your Databases**
   ```python
   # Using Python SDK
   from src.sdk.client import DiscovererClient
   
   client = DiscovererClient(base_url="http://discoverer-service:8000")
   
   await client.register_database(
       id="production_db",
       type="postgresql",
       host="db.example.com",
       port=5432,
       database="mydb",
       user="user",
       password="password"
   )
   ```

3. **Query from Your Application**
   ```python
   # In your application code
   result = await client.execute_query("Show me all active users")
   print(result.data)  # Query results
   print(result.chart)  # Auto-generated visualization
   ```

### Option 2: Embedded Library

Import The Discoverer as a Python library directly into your application.

**Best for:**
- Single application use
- Tight integration requirements
- Custom deployment scenarios

**Implementation Steps:**

1. **Install as Package**
   ```bash
   pip install the-discoverer
   # Or from source
   pip install -e .
   ```

2. **Use in Your Code**
   ```python
   from src.application.services.discovery_service import DiscoveryService
   from src.application.services.query_service import QueryService
   
   # Initialize services
   discovery = DiscoveryService(...)
   query_service = QueryService(...)
   
   # Register database
   await discovery.discover_database({
       "id": "my_db",
       "type": "postgresql",
       "host": "localhost",
       "database": "mydb"
   })
   
   # Execute queries
   result = await query_service.execute_query("Count all orders")
   ```

### Option 3: API Integration

Call The Discoverer REST API directly from any application.

**Best for:**
- Non-Python applications
- Microservices architecture
- Existing API infrastructure

**Implementation Steps:**

1. **Deploy The Discoverer Service** (same as Option 1)

2. **Call API from Your Application**
   ```javascript
   // JavaScript/TypeScript example
   const response = await fetch('http://discoverer-service:8000/api/query/execute', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       query: "Show me all customers"
     })
   });
   
   const result = await response.json();
   ```

### Option 4: CLI Integration

Use The Discoverer CLI in scripts and automation pipelines.

**Best for:**
- Automation scripts
- CI/CD pipelines
- Scheduled reports

**Implementation Steps:**

1. **Install CLI**
   ```bash
   pip install -e .
   ```

2. **Use in Scripts**
   ```bash
   # Register database
   discoverer register --database-id db1 --type postgresql \
     --host-db localhost --port 5432 --database mydb
   
   # Execute query
   discoverer query "Show sales by category" --format json
   
   # Export results
   discoverer export query_id --format csv --output sales.csv
   ```

## 🏗️ Architecture Overview

The Discoverer follows clean architecture principles:

```
┌─────────────────────────────────────────┐
│         Your Application                 │
│  (Python, JavaScript, CLI, etc.)        │
└──────────────┬──────────────────────────┘
               │
               │ API / SDK
               │
┌──────────────▼──────────────────────────┐
│      The Discoverer Service             │
│  ┌──────────────────────────────────┐  │
│  │  API Layer (FastAPI)             │  │
│  └──────────────┬───────────────────┘  │
│  ┌──────────────▼───────────────────┐  │
│  │  Application Services            │  │
│  │  - Query Service                 │  │
│  │  - Discovery Service             │  │
│  │  - Visualization Service         │  │
│  └──────────────┬───────────────────┘  │
│  ┌──────────────▼───────────────────┐  │
│  │  Infrastructure                 │  │
│  │  - Database Adapters            │  │
│  │  - Vector DB (Qdrant)           │  │
│  │  - LLM (OpenAI)                 │  │
│  │  - Cache (Redis)                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
               │
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌─────▼────┐
│ Your   │         │ Vector   │
│ DBs    │         │ DB       │
│        │         │ (Qdrant) │
└────────┘         └──────────┘
```

## 🎓 Quick Start Guide

### 1. Prerequisites

- Python 3.10+
- Docker and Docker Compose
- OpenAI API key (for AI features)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/khannoussi-malek/the-discoverer.git
cd the-discoverer

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start services (Redis, Qdrant)
docker-compose up -d

# Initialize vector database
python scripts/setup_vector_db.py

# Start the service
uvicorn src.api.main:app --reload
```

### 3. Register Your First Database

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

### 4. Execute Your First Query

```bash
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all customers"
  }'
```

### 5. View API Documentation

Open http://localhost:8000/docs in your browser for interactive API documentation.

## 📚 Documentation

📖 **[Complete Documentation Index](docs/README.md)** - Start here for comprehensive guides

**Essential Guides:**
- [🚀 Getting Started Guide](docs/GETTING_STARTED.md) - Detailed setup instructions
- [💡 Examples](docs/EXAMPLES.md) - Real-world usage examples
- [📡 API Reference](docs/API.md) - Complete API documentation
- [🐍 Python SDK](docs/SDK.md) - Python integration guide
- [🌐 JavaScript SDK](docs/JAVASCRIPT_SDK.md) - JavaScript/TypeScript integration

**Feature Guides:**
- [📊 Dashboards](docs/DASHBOARDS.md) - Create and share dashboards
- [⏰ Scheduler](docs/SCHEDULER.md) - Automate query execution
- [🔔 Webhooks](docs/WEBHOOKS.md) - Event notifications
- [🚢 Deployment](docs/DEPLOYMENT.md) - Production deployment

## 🛠️ Supported Databases

- ✅ **PostgreSQL** - Full support with schema relationships
- ✅ **MySQL** - Complete schema discovery
- ✅ **MongoDB** - Document schema inference
- ✅ **SQLite** - Lightweight database support
- ✅ **Cassandra** - NoSQL column-family support
- ✅ **Elasticsearch** - Search engine integration

## 🎨 Features at a Glance

### Query Features
- Natural language to SQL/NoSQL conversion
- Multi-database querying
- Query result caching
- Query optimization suggestions
- Query versioning and comparison
- Query result streaming
- Batch query execution

### Visualization Features
- 15+ chart types
- Automatic chart type detection
- Chart templates
- Dashboard creation
- Chart export (PNG, PDF, HTML, SVG)

### Integration Features
- REST API with OpenAPI docs
- Python SDK (async & sync)
- JavaScript/TypeScript SDK
- WebSocket support
- CLI tool
- Webhooks

### Enterprise Features
- JWT authentication
- API key management
- Rate limiting
- Cost tracking
- Prometheus metrics
- Health monitoring
- Connection pooling
- Query scheduling

## 🔧 Development

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

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black src/
flake8 src/
mypy src/
```

## 📊 API Endpoints Overview

- `/api/discovery/*` - Database discovery and management
- `/api/query/*` - Query execution and analysis
- `/api/visualization/*` - Chart generation
- `/api/dashboards/*` - Dashboard management
- `/api/scheduler/*` - Query scheduling
- `/api/webhooks/*` - Webhook management
- `/api/sharing/*` - Query result sharing
- `/api/export/*` - Data export (CSV, JSON, Excel, Parquet, Avro)
- `/api/auth/*` - Authentication
- `/api/metrics/prometheus` - Prometheus metrics
- `/health` - Health checks

See [API Reference](docs/API.md) for complete documentation.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👤 Author

**Malek Khannoussi**

- GitHub: [@khannoussi-malek](https://github.com/khannoussi-malek)
- LinkedIn: [khannoussi-malek](https://www.linkedin.com/in/khannoussi-malek/)

## 📄 License

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

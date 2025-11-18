# The Discoverer - Documentation Index

Welcome to The Discoverer documentation! This index will help you navigate through all available guides and find exactly what you need.

## 🎯 What is The Discoverer?

**The Discoverer** is an AI-powered database discovery and query platform that transforms how you interact with your databases. Instead of writing complex SQL queries, you simply ask questions in natural language, and The Discoverer automatically:

- **Discovers** your database schemas across multiple database types (PostgreSQL, MySQL, MongoDB, etc.)
- **Understands** your data structure using AI and vector search
- **Generates** optimized queries from natural language
- **Executes** queries across multiple databases simultaneously
- **Visualizes** results with beautiful, interactive charts
- **Shares** insights with your team through dashboards and exports

### Key Benefits

✅ **No SQL Knowledge Required** - Ask questions in plain English  
✅ **Multi-Database Support** - Query PostgreSQL, MySQL, MongoDB, SQLite, Cassandra, Elasticsearch  
✅ **Fast Discovery** - AI-powered schema discovery with vector search  
✅ **Automatic Visualization** - 15+ chart types generated automatically  
✅ **Easy Integration** - REST API, Python SDK, JavaScript SDK, CLI  
✅ **Enterprise Ready** - Authentication, scheduling, webhooks, monitoring  

## 🚀 How to Implement The Discoverer

### Option 1: Standalone Service (Recommended)

Deploy The Discoverer as a separate microservice that your applications connect to.

**Best for:** Multiple applications, centralized data access, team collaboration

**Quick Start:**
1. Follow the [Getting Started Guide](GETTING_STARTED.md) to deploy the service
2. Register your databases via API or configuration file
3. Integrate using [Python SDK](SDK.md), [JavaScript SDK](JAVASCRIPT_SDK.md), or REST API
4. Start querying with natural language!

### Option 2: Embedded Library

Import The Discoverer as a Python library directly into your application.

**Best for:** Single application use, tight integration requirements

**Quick Start:**
1. Install: `pip install the-discoverer`
2. Import and use services directly in your code
3. See [Python SDK](SDK.md) for examples

### Option 3: API Integration

Call The Discoverer REST API directly from any application.

**Best for:** Non-Python applications, microservices architecture

**Quick Start:**
1. Deploy The Discoverer service
2. Call REST API endpoints from your application
3. See [API Reference](API.md) for complete endpoint documentation

### Option 4: CLI Tool

Use The Discoverer CLI in scripts and automation pipelines.

**Best for:** Automation scripts, CI/CD pipelines, scheduled reports

**Quick Start:**
1. Install: `pip install -e .`
2. Use CLI commands in your scripts
3. See [CLI Documentation](CLI.md) for all commands

## 📚 Quick Start

**New to The Discoverer?** Start here:

1. **[Getting Started Guide](GETTING_STARTED.md)** - Complete setup instructions (5 minutes)
   - Installation and prerequisites
   - First database registration
   - Your first query
   - Common workflows

2. **[Examples](EXAMPLES.md)** - Real-world usage examples
   - Database registration examples
   - Query execution patterns
   - API usage samples
   - Python and JavaScript SDK examples

---

## 📚 Learning Paths

### For First-Time Users

1. **Start Here**: [Getting Started Guide](GETTING_STARTED.md)
2. **See Examples**: [Examples](EXAMPLES.md)
3. **Understand Architecture**: [Architecture Overview](ARCHITECTURE.md)
4. **Explore API**: [API Reference](API.md)

### For Developers

1. **Setup**: [Getting Started Guide](GETTING_STARTED.md)
2. **SDK Integration**: 
   - [Python SDK](SDK.md) - Async and sync Python clients
   - [JavaScript/TypeScript SDK](JAVASCRIPT_SDK.md) - Browser and Node.js support
3. **API Reference**: [Complete API Documentation](API.md)
4. **Architecture**: [System Architecture](ARCHITECTURE.md)

### For DevOps/Administrators

1. **Deployment**: [Deployment Guide](DEPLOYMENT.md)
2. **Monitoring**: [Metrics & Monitoring](METRICS.md)
3. **Connection Management**: [Connection Pools](CONNECTION_POOLS.md)
4. **Health Checks**: See [API Reference - Health Endpoints](API.md#health-endpoints)

---

## 📖 Core Documentation

### Essential Guides

| Document | Description | When to Use |
|----------|-------------|-------------|
| **[Getting Started](GETTING_STARTED.md)** | Quick setup and first steps | First time setup |
| **[Examples](EXAMPLES.md)** | Code samples and usage patterns | Learning how to use features |
| **[API Reference](API.md)** | Complete API endpoint documentation | Building integrations |
| **[Architecture](ARCHITECTURE.md)** | System design and architecture | Understanding the system |

### Feature Guides

| Feature | Documentation | Use Case |
|---------|---------------|----------|
| **Dashboards** | [Dashboards Guide](DASHBOARDS.md) | Creating and managing dashboards |
| **Chart Templates** | [Chart Templates](CHART_TEMPLATES.md) | Reusable chart configurations |
| **Query Sharing** | [Query Result Sharing](QUERY_RESULT_SHARING.md) | Sharing query results securely |
| **Webhooks** | [Webhooks Guide](WEBHOOKS.md) | Event notifications and integrations |
| **Scheduler** | [Scheduler Guide](SCHEDULER.md) | Automated query execution |
| **Query Versioning** | [Query Versioning](QUERY_VERSIONING.md) | Tracking query changes |
| **Connection Pools** | [Connection Pools](CONNECTION_POOLS.md) | Database connection management |
| **Compression** | [Compression Guide](COMPRESSION.md) | Data compression utilities |
| **WebSocket** | [WebSocket Guide](WEBSOCKET.md) | Real-time updates |
| **Chart Export** | [Chart Export](CHART_EXPORT.md) | Exporting visualizations |
| **CLI Tool** | [CLI Documentation](CLI.md) | Command-line interface |

### SDK Documentation

| SDK | Documentation | Platform |
|-----|---------------|----------|
| **Python SDK** | [Python SDK Guide](SDK.md) | Python 3.10+ |
| **JavaScript/TypeScript SDK** | [JavaScript SDK Guide](JAVASCRIPT_SDK.md) | Browser & Node.js |

### Operations & Deployment

| Topic | Documentation | Purpose |
|-------|---------------|---------|
| **Deployment** | [Deployment Guide](DEPLOYMENT.md) | Production deployment |
| **Metrics** | [Metrics & Monitoring](METRICS.md) | Performance monitoring |
| **Features** | [Features Overview](FEATURES.md) | Complete feature list |

---

## 🎯 Common Use Cases

### Use Case 1: "I want to query my databases with natural language"

**Path:**
1. [Getting Started](GETTING_STARTED.md) - Setup and register your first database
2. [Examples](EXAMPLES.md#query-execution) - See query examples
3. [API Reference - Query Endpoints](API.md#query-endpoints) - Full query API

**Key Features:**
- Natural language to SQL/NoSQL conversion
- Multi-database querying
- Query result pagination and streaming

---

### Use Case 2: "I want to build a dashboard with visualizations"

**Path:**
1. [Dashboards Guide](DASHBOARDS.md) - Create your first dashboard
2. [Chart Templates](CHART_TEMPLATES.md) - Use reusable chart configurations
3. [Chart Export](CHART_EXPORT.md) - Export visualizations

**Key Features:**
- Dashboard creation and management
- Multiple chart types (bar, line, pie, scatter, etc.)
- Widget-based layouts
- Public/private dashboards

---

### Use Case 3: "I want to integrate The Discoverer into my application"

**Path:**
1. Choose your SDK:
   - [Python SDK](SDK.md) - For Python applications
   - [JavaScript SDK](JAVASCRIPT_SDK.md) - For web/Node.js applications
2. [API Reference](API.md) - Direct REST API integration
3. [Examples](EXAMPLES.md) - Integration examples

**Key Features:**
- Full-featured SDKs (async and sync)
- REST API with OpenAPI documentation
- WebSocket support for real-time updates

---

### Use Case 4: "I want to automate query execution"

**Path:**
1. [Scheduler Guide](SCHEDULER.md) - Schedule queries with cron-like syntax
2. [Webhooks Guide](WEBHOOKS.md) - Get notified of query completion
3. [Export Templates](API.md#export-templates) - Automated exports

**Key Features:**
- Cron-based scheduling
- Webhook notifications
- Scheduled exports
- Background job execution

---

### Use Case 5: "I want to share query results with my team"

**Path:**
1. [Query Result Sharing](QUERY_RESULT_SHARING.md) - Create shareable links
2. [Dashboards](DASHBOARDS.md) - Create shared dashboards
3. [API Reference - Sharing Endpoints](API.md#sharing-endpoints)

**Key Features:**
- Secure shareable links
- Password protection
- Access limits and expiration
- Email restrictions

---

### Use Case 6: "I want to monitor and optimize performance"

**Path:**
1. [Metrics & Monitoring](METRICS.md) - Prometheus metrics
2. [Connection Pools](CONNECTION_POOLS.md) - Optimize connections
3. [API Reference - Stats Endpoints](API.md#stats-endpoints)

**Key Features:**
- Prometheus metrics export
- Performance statistics
- Connection pool management
- Health monitoring

---

## 🔍 Feature Reference

### Query Features
- ✅ Natural language queries
- ✅ Multi-database support
- ✅ Query result caching
- ✅ Query optimization
- ✅ Query versioning
- ✅ Query result comparison
- ✅ Query streaming (NDJSON, JSON, CSV, TSV)
- ✅ Query result compression
- ✅ Query result pagination

**Documentation:**
- [API Reference - Query](API.md#query-endpoints)
- [Examples - Query Execution](EXAMPLES.md#query-execution)
- [Query Versioning](QUERY_VERSIONING.md)

### Visualization Features
- ✅ Automatic chart generation
- ✅ Chart templates
- ✅ Dashboard creation
- ✅ Multiple chart types (10+)
- ✅ Chart export (PNG, PDF, HTML, SVG)

**Documentation:**
- [Dashboards Guide](DASHBOARDS.md)
- [Chart Templates](CHART_TEMPLATES.md)
- [Chart Export](CHART_EXPORT.md)

### Integration Features
- ✅ REST API
- ✅ Python SDK (async & sync)
- ✅ JavaScript/TypeScript SDK
- ✅ WebSocket support
- ✅ Webhooks
- ✅ CLI tool

**Documentation:**
- [Python SDK](SDK.md)
- [JavaScript SDK](JAVASCRIPT_SDK.md)
- [Webhooks Guide](WEBHOOKS.md)
- [WebSocket Guide](WEBSOCKET.md)
- [CLI Documentation](CLI.md)

### Data Management Features
- ✅ Export (CSV, JSON, Excel, Parquet, Avro)
- ✅ Export templates
- ✅ Scheduled exports
- ✅ Query result sharing
- ✅ Data compression

**Documentation:**
- [API Reference - Export](API.md#export-endpoints)
- [Compression Guide](COMPRESSION.md)
- [Query Result Sharing](QUERY_RESULT_SHARING.md)

### Administration Features
- ✅ Database health monitoring
- ✅ Schema change detection
- ✅ Connection pool management
- ✅ API key management
- ✅ Cost tracking (LLM usage)
- ✅ Authentication & authorization

**Documentation:**
- [Connection Pools](CONNECTION_POOLS.md)
- [API Reference - Management](API.md#management-endpoints)
- [Metrics & Monitoring](METRICS.md)

---

## 🛠️ API Endpoints Quick Reference

### Core Endpoints
- **Discovery**: `/api/discovery/*` - Database discovery and management
- **Query**: `/api/query/*` - Query execution
- **Visualization**: `/api/visualization/*` - Chart generation
- **Export**: `/api/export/*` - Export query results

### Advanced Endpoints
- **Dashboards**: `/api/dashboards/*` - Dashboard management
- **Chart Templates**: `/api/chart-templates/*` - Chart template management
- **Sharing**: `/api/sharing/*` - Query result sharing
- **Webhooks**: `/api/webhooks/*` - Webhook management
- **Scheduler**: `/api/scheduler/*` - Query scheduling
- **Cache**: `/api/cache/*` - Cache management
- **Pools**: `/api/pools/*` - Connection pool management

**Full Reference**: [API Documentation](API.md)

---

## 📱 SDK Quick Start

### Python SDK

```python
from src.sdk.client import DiscovererClient

client = DiscovererClient(base_url="http://localhost:8000")
result = await client.execute_query("Show me all customers")
```

**Full Guide**: [Python SDK Documentation](SDK.md)

### JavaScript SDK

```javascript
import { DiscovererClient } from '@the-discoverer/sdk';

const client = new DiscovererClient({ baseURL: 'http://localhost:8000' });
const result = await client.executeQuery('Show me all customers');
```

**Full Guide**: [JavaScript SDK Documentation](JAVASCRIPT_SDK.md)

---

## 🚦 Getting Help

### Documentation Issues
- Check the [Getting Started Guide](GETTING_STARTED.md) for setup help
- Review [Examples](EXAMPLES.md) for usage patterns
- Consult [API Reference](API.md) for endpoint details

### Common Tasks
- **Setup Problems**: [Getting Started - Troubleshooting](GETTING_STARTED.md#troubleshooting)
- **API Questions**: [API Reference](API.md)
- **Integration Help**: [SDK Documentation](SDK.md) or [JavaScript SDK](JAVASCRIPT_SDK.md)

---

## 📋 Documentation Structure

```
docs/
├── README.md (this file)          # Navigation index
├── GETTING_STARTED.md              # Quick start guide
├── EXAMPLES.md                     # Usage examples
├── API.md                          # Complete API reference
├── ARCHITECTURE.md                 # System architecture
├── DEPLOYMENT.md                   # Deployment guide
├── FEATURES.md                     # Features overview
│
├── SDK.md                          # Python SDK
├── JAVASCRIPT_SDK.md               # JavaScript/TypeScript SDK
├── CLI.md                          # CLI tool
│
├── DASHBOARDS.md                   # Dashboard creation
├── CHART_TEMPLATES.md              # Chart templates
├── CHART_EXPORT.md                 # Chart export
├── QUERY_RESULT_SHARING.md         # Result sharing
├── QUERY_VERSIONING.md             # Query versioning
├── WEBHOOKS.md                     # Webhooks
├── WEBSOCKET.md                    # WebSocket support
├── SCHEDULER.md                    # Query scheduling
├── CONNECTION_POOLS.md             # Connection pools
├── COMPRESSION.md                  # Data compression
└── METRICS.md                      # Metrics & monitoring
```

---

## 🎓 Learning Resources

### Beginner Path
1. Read [Getting Started Guide](GETTING_STARTED.md)
2. Try [Examples](EXAMPLES.md)
3. Explore [API Documentation](API.md)

### Intermediate Path
1. Build a dashboard: [Dashboards Guide](DASHBOARDS.md)
2. Integrate with SDK: [Python SDK](SDK.md) or [JavaScript SDK](JAVASCRIPT_SDK.md)
3. Set up webhooks: [Webhooks Guide](WEBHOOKS.md)

### Advanced Path
1. Understand architecture: [Architecture Guide](ARCHITECTURE.md)
2. Optimize performance: [Connection Pools](CONNECTION_POOLS.md), [Metrics](METRICS.md)
3. Deploy to production: [Deployment Guide](DEPLOYMENT.md)

---

## 🔗 Quick Links

- **Repository**: [GitHub](https://github.com/khannoussi-malek/the-discoverer)
- **API Docs (when running)**: http://localhost:8000/docs
- **ReDoc (when running)**: http://localhost:8000/redoc

---

**Last Updated**: 2024

**Need help?** Start with the [Getting Started Guide](GETTING_STARTED.md) or check the [Examples](EXAMPLES.md) for code samples.


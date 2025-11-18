# Changelog

## [Unreleased]

### Added
- MongoDB query generator with pattern matching and LLM support
- Cassandra database adapter and CQL query generator
- Elasticsearch database adapter and query generator
- Query streaming support (NDJSON format) in query API
- Integration tests for database adapters, vector DB, query service, and LLM generators
- JWT authentication infrastructure (basic structure for future use)
- Support for NoSQL query execution (MongoDB, Elasticsearch) in query service
- Enhanced query route with streaming capability
- **Query templates/saved queries** - Save and reuse queries with parameters
- **Export functionality** - Export query results to CSV, JSON, and Excel formats
- **Query result pagination** - Paginate large result sets with page/page_size parameters
- Query template API endpoints (create, list, get, execute, search, delete)
- Export API endpoints (export query results, export arbitrary data)
- **Query optimization utilities** - SQL analysis, index suggestions, complexity estimation
- **Batch query execution** - Execute multiple queries in parallel or sequentially
- **Circuit breaker pattern** - Fault tolerance for database connections
- **Performance benchmarking** - Benchmark runner for performance testing
- Query optimization API endpoints (analyze, suggest-indexes, complexity)
- Batch query API endpoint
- **Query scheduling** - Schedule queries to run automatically (hourly, daily, weekly, monthly, custom cron)
- **Prometheus metrics** - Production-ready metrics collection and export
- Scheduler API endpoints (create, list, execute, pause, resume, delete schedules)
- Prometheus metrics endpoint (`/api/metrics/prometheus`)
- **Server-side pagination** - Database-level pagination for better performance
- **WebSocket support** - Real-time query updates and notifications
- Pagination service with SQL query building
- WebSocket connection manager for real-time updates
- Pagination API endpoint for direct SQL queries
- **Query result transformation** - Transform, filter, sort, aggregate query results
- **Analytics and usage tracking** - Track query usage, performance, and database statistics
- Transformation API endpoints (transform, preview)
- Analytics API endpoints (stats, top-queries, database analytics)
- **CLI Tool** - Command-line interface for The Discoverer
- **Enhanced Authentication** - User registration, login, JWT tokens, user management
- CLI commands (register, list, query, health, sync, export)
- Authentication API endpoints (register, login, me, users)
- **Advanced visualization** - Additional chart types (heatmap, box, violin, 3D scatter, surface, sunburst, treemap, funnel, gauge, waterfall)
- **Python SDK** - Async and sync clients for easy integration
- Advanced visualization service with extended chart types
- Python SDK with full API coverage (async and sync clients)
- **Chart export** - Export charts to PNG, PDF, HTML, SVG formats
- **Query versioning** - Track and compare different versions of queries
- Chart export API endpoint (`/api/visualization/export/{query_id}`)
- Query versioning API endpoints (list versions, get version, compare versions, set current)
- **Database health monitoring** - Automatic health checks and reconnection
- **Schema change detection** - Track and detect database schema changes
- Health monitoring API endpoints (`/health/databases`, `/health/databases/{id}`)
- Automatic background health monitoring with configurable intervals
- **API key management** - Create, manage, and authenticate with API keys
- API key authentication support (X-API-Key header)
- API key scopes and rate limiting
- API key expiration and revocation
- **Query result comparison** - Compare results from different queries
- Query comparison API endpoint (`/api/comparison/compare`)
- Similarity scoring and difference detection
- **JavaScript/TypeScript SDK** - Client library for browser and Node.js
- Full TypeScript support with type definitions
- Browser and Node.js compatibility
- **Chart templates** - Reusable chart configurations
- Chart template API endpoints (create, list, get, update, delete, apply, search)
- Template usage tracking and public/private templates
- **Parquet export** - Export data to Parquet format
- **Dashboard creation** - Create and manage dashboards with widgets
- Dashboard API endpoints (create, list, get, update, delete, render, widget management)
- Dashboard widget support (charts, queries, metrics, text)
- **Query result sharing** - Share query results with secure links
- Shareable links with expiration and access limits
- Password-protected shares
- Share management API endpoints
- **Query result caching strategies** - Advanced caching with TTL, LRU eviction, and statistics
- Cache management API endpoints (stats, invalidate, clear)
- **Cost tracking** - LLM API usage and cost tracking
- Cost tracking API endpoints (stats, total, by-model, by-operation, daily)
- **REST API webhooks** - Webhook system for event notifications
- Webhook management API endpoints (create, list, get, update, delete, test)
- Webhook event types (query.completed, query.failed, database.registered, etc.)
- Webhook signature verification for security
- Automatic webhook triggering on events
- **Query result compression** - Compress query results to reduce response size
- Multiple compression algorithms (gzip, zlib, lzma, brotli)
- Compression statistics and analysis
- Compression API endpoints (compress, decompress, stats)
- **Database connection pooling per database** - Per-database connection pool management
- Pool configuration and monitoring
- Pool statistics and health checks
- Pool management API endpoints (list, get, config, refresh, close, initialize)
- **Avro export** - Export data to Apache Avro format
- Avro schema inference from data
- Avro-compatible type conversion
- **Query result streaming improvements** - Enhanced streaming with multiple formats and progress
- Multiple streaming formats (NDJSON, JSON, CSV, TSV)
- Progress updates during streaming
- Chunked streaming for better performance
- Improved streaming API with format options
- **Export templates** - Reusable export configurations
- Template-based data filtering, sorting, and formatting
- Custom filename patterns with placeholders
- Column selection and mapping
- Export template management API endpoints
- **Scheduled exports** - Automatically export query results on a schedule
- Scheduled export management API endpoints
- Integration with export templates
- File storage and destination delivery (webhooks)
- Failure notifications

### Changed
- MongoDB adapter now accepts JSON string queries (matching generator output)
- Query service handles different query types (SQL, MongoDB, Elasticsearch, CQL)
- Query route supports streaming responses via `stream` query parameter

### Fixed
- MongoDB query execution to properly parse JSON queries from generators

## [1.0.0] - Initial Release

### Added

#### Core Features
- Multi-database support (PostgreSQL, MySQL, MongoDB)
- Vector database integration (Qdrant) for schema and content
- AI-powered query generation with OpenAI
- Pattern matching for simple queries (avoids LLM calls)
- Hybrid query routing (content vector DB + schema-based)
- Automatic visualization generation with Plotly
- Multi-layer caching (in-memory + Redis)
- Parallel query execution across databases
- Connection pooling per database type
- Batch operations for embeddings and vector inserts
- Performance monitoring and statistics
- Comprehensive error handling with custom exceptions
- Request logging middleware
- Health check endpoints
- Database configuration validation
- Content indexing with smart strategies
- Incremental schema updates
- Clean architecture with design patterns
- Complete API documentation
- Docker setup with docker-compose
- Makefile for common tasks

#### Additional Features
- SQLite database adapter
- Query history tracking and search
- Rate limiting (60 requests/minute)
- Database health monitoring with background checks
- Request ID middleware for request tracking
- Query analysis endpoint
- SQL safety validation
- Configuration file loading (YAML)
- Management API endpoints
- Health check API endpoints
- Exponential backoff utilities
- Query analyzer for metadata extraction
- Enhanced error handling and validation

### Infrastructure
- PostgreSQL adapter with full schema extraction
- MongoDB adapter with document schema inference
- MySQL adapter
- Qdrant vector database client
- Sentence transformers for embeddings
- OpenAI LLM integration
- Redis caching layer

### API
- Discovery endpoints (register, list, sync databases)
- Query endpoints (execute natural language queries)
- Visualization endpoints (generate charts)
- Indexing endpoints (index table content)
- Statistics endpoints (performance metrics)

### Documentation
- Architecture documentation
- API documentation
- Usage examples
- Deployment guide
- Implementation summary


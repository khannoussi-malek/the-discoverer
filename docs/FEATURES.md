# Features Documentation

## Core Features

### 1. Multi-Database Support

The Discoverer supports multiple database types:

- **PostgreSQL**: Full schema extraction with relationships
- **MySQL**: Complete schema discovery
- **MongoDB**: Document schema inference from samples
- **SQLite**: Lightweight database support

All adapters follow the same interface, making it easy to add new database types.

### 2. Vector Database Integration

#### Schema Vector DB
- Tables, columns, and relationships indexed
- Fast semantic search for schema discovery
- Batch indexing for performance

#### Content Vector DB
- Selective indexing of frequently queried data
- Smart indexing strategies (full, sampled, aggregated)
- Hybrid query routing

### 3. AI-Powered Query Generation

- **Pattern Matching**: Instant responses for simple queries (no LLM call)
- **LLM Generation**: OpenAI GPT models for complex queries
- **Model Selection**: Automatically chooses GPT-3.5 or GPT-4 based on complexity
- **SQL Cleaning**: Removes markdown and formats SQL properly

### 4. Performance Optimizations

- **Multi-layer Caching**: In-memory → Redis → Vector DB
- **Parallel Execution**: Queries across multiple databases run in parallel
- **Connection Pooling**: Per-database connection pools
- **Batch Operations**: Embeddings and vector inserts batched
- **Smart Database Selection**: Only queries relevant databases

### 5. Query History

- Automatic query logging
- Search query history
- Query statistics and analytics
- Per-database query tracking

### 6. Rate Limiting

- Configurable requests per minute
- Per-client rate limiting
- Rate limit headers in responses

### 7. Error Handling

- Custom exception hierarchy
- Structured error responses
- Validation at service boundaries
- Comprehensive error logging

### 8. Visualization

- Automatic chart type detection
- Multiple chart types (bar, line, pie, scatter, table)
- Plotly integration for interactive charts

## API Features

### Discovery API
- Register databases
- List all databases
- Sync database schemas
- Database health checks

### Query API
- Execute natural language queries
- Query specific databases or auto-select
- Cached results
- Execution time tracking

### Visualization API
- Generate charts from query results
- Custom chart configuration
- Multiple output formats

### Indexing API
- Index table content to vector DB
- Multiple indexing strategies
- Incremental updates

### History API
- View query history
- Search past queries
- Query statistics
- Per-database history

### Statistics API
- Performance metrics
- Operation timings (p50, p95, p99)
- Reset statistics

## Configuration

### Environment Variables
- Database connections
- Vector DB settings
- LLM configuration
- Cache settings
- Performance tuning

### YAML Configuration
- Load databases from file
- Environment variable substitution
- Metadata and tags

## Security Features

- Rate limiting
- Input validation
- Error message sanitization
- CORS configuration

## Monitoring

- Request logging
- Performance monitoring
- Health checks
- Query statistics


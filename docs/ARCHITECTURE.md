# Architecture Documentation

## Overview

The Discoverer follows a clean architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────┐
│      Presentation Layer (API)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Application Layer (Services)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Domain Layer (Models)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Infrastructure Layer            │
└─────────────────────────────────────┘
```

## Layers

### Domain Layer
Pure business entities with no dependencies. Simple data classes representing:
- Database
- Schema
- Query
- Result
- Visualization

### Application Layer
Business logic and orchestration:
- DiscoveryService: Database discovery and schema extraction
- QueryService: Query execution and result aggregation
- VisualizationService: Chart generation

### Infrastructure Layer
External system integrations:
- Database adapters (PostgreSQL, MongoDB, MySQL)
- Vector database client (Qdrant)
- LLM client (OpenAI)
- Cache repository (Multi-layer)

### Presentation Layer
FastAPI REST API with:
- Discovery endpoints
- Query endpoints
- Visualization endpoints

## Design Patterns

### Repository Pattern
Abstracts data access (DatabaseRepository, VectorDBRepository, CacheRepository)

### Adapter Pattern
Database abstraction (DatabaseAdapter with implementations)

### Factory Pattern
Object creation (DatabaseAdapterFactory, QueryGeneratorFactory)

### Strategy Pattern
Query generation algorithms (QueryGenerator with implementations)

## Performance Optimizations

1. **Multi-layer caching**: In-memory → Redis → Vector DB
2. **Parallel execution**: Queries executed in parallel across databases
3. **Connection pooling**: Per-database connection pools
4. **Batch operations**: Embeddings and vector inserts batched
5. **Pattern matching**: Simple queries avoid LLM calls

## Vector Database Strategy

- **Schema Vector DB**: Tables, columns, relationships indexed
- **Content Vector DB**: Selective indexing of frequently queried data
- **Hybrid routing**: Smart query routing based on query type


# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Discovery

#### Register Database
```
POST /api/discovery/databases
```

Request body:
```json
{
  "id": "my_db",
  "type": "postgresql",
  "name": "My Database",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "user",
  "password": "password",
  "metadata": {
    "description": "Production database",
    "tags": ["production"]
  }
}
```

#### List Databases
```
GET /api/discovery/databases
```

#### Sync Database Schema
```
POST /api/discovery/databases/{db_id}/sync
```

### Query

#### Execute Query
```
POST /api/query/execute
```

Request body:
```json
{
  "query": "Show me all customers",
  "database_ids": ["db1", "db2"]  // Optional
}
```

Response:
```json
{
  "query_id": "uuid",
  "data": [...],
  "total_rows": 100,
  "execution_time": 0.5,
  "databases_queried": ["db1"],
  "cached": false
}
```

### Visualization

#### Generate Visualization
```
POST /api/visualization/generate
```

Request body:
```json
{
  "query_id": "uuid",
  "chart_type": "bar",
  "x_axis": "category",
  "y_axis": "value",
  "title": "Sales by Category"
}
```

## Authentication

Currently no authentication required. Add JWT tokens for production.


# Query Versioning Documentation

## Overview

Query versioning allows you to track different versions of queries over time, compare them, and manage which version is currently active. This is useful for:
- Tracking query evolution
- Comparing query performance
- Reverting to previous versions
- Auditing query changes

## API Endpoints

### List All Versions

```http
GET /api/versioning/{query_id}/versions
```

**Response:**
```json
{
  "query_id": "query-123",
  "total_versions": 3,
  "versions": [
    {
      "id": "version-1",
      "version": 1,
      "query_text": "Count users",
      "generated_query": "SELECT COUNT(*) FROM users",
      "result_hash": "abc123...",
      "created_at": "2024-01-01T10:00:00",
      "created_by": "user1",
      "notes": "Initial version",
      "is_current": false
    }
  ]
}
```

### Get Current Version

```http
GET /api/versioning/{query_id}/current
```

Returns the currently active version of a query.

### Get Specific Version

```http
GET /api/versioning/{query_id}/versions/{version}
```

Returns details of a specific version number.

### Set Current Version

```http
POST /api/versioning/{query_id}/versions/{version}/set-current
```

Marks a specific version as the current/active version.

**Response:**
```json
{
  "message": "Version 2 set as current"
}
```

### Compare Versions

```http
GET /api/versioning/{query_id}/compare?version1=1&version2=2
```

**Response:**
```json
{
  "query_id": "query-123",
  "version1": {
    "version": 1,
    "query_text": "Count users",
    "generated_query": "SELECT COUNT(*) FROM users",
    "result_hash": "abc123...",
    "created_at": "2024-01-01T10:00:00"
  },
  "version2": {
    "version": 2,
    "query_text": "Count active users",
    "generated_query": "SELECT COUNT(*) FROM users WHERE active = true",
    "result_hash": "def456...",
    "created_at": "2024-01-02T10:00:00"
  },
  "differences": {
    "query_text_changed": true,
    "generated_query_changed": true,
    "result_changed": true
  }
}
```

## Usage Examples

### Creating Versions

Versions are automatically created when queries are executed. The versioning system tracks:
- Original user query text
- Generated SQL/NoSQL query
- Result hash (for comparison)
- Timestamp
- Creator (if authenticated)
- Notes (optional)

### Comparing Query Results

```bash
# Compare two versions
curl "http://localhost:8000/api/versioning/query-123/compare?version1=1&version2=2"
```

This helps identify:
- Whether the query text changed
- Whether the generated query changed
- Whether the results changed (via hash comparison)

### Setting Current Version

```bash
# Set version 2 as current
curl -X POST "http://localhost:8000/api/versioning/query-123/versions/2/set-current"
```

### Listing All Versions

```bash
# Get all versions
curl "http://localhost:8000/api/versioning/query-123/versions"
```

## Python SDK Usage

```python
from src.sdk.sync_client import DiscovererSyncClient, DiscovererConfig

with DiscovererSyncClient(DiscovererConfig()) as client:
    # Execute query (creates version 1)
    result1 = client.execute_query("Count users")
    
    # Execute modified query (creates version 2)
    result2 = client.execute_query("Count active users")
    
    # Compare versions
    comparison = client.client.get(
        f"/api/versioning/{result1['query_id']}/compare",
        params={"version1": 1, "version2": 2}
    ).json()
    
    print(f"Query changed: {comparison['differences']['query_text_changed']}")
    print(f"Results changed: {comparison['differences']['result_changed']}")
```

## Use Cases

1. **Query Evolution Tracking**: See how queries change over time
2. **Performance Comparison**: Compare results between versions
3. **Rollback**: Revert to a previous query version
4. **Audit Trail**: Track who changed what and when
5. **Debugging**: Compare working vs. broken query versions

## Implementation Details

- Versions are stored in-memory (can be extended to persistent storage)
- Result hashing uses SHA-256 for fast comparison
- Version numbers are sequential (1, 2, 3, ...)
- Only one version can be "current" at a time
- Versions are automatically created on query execution

## Future Enhancements

- Persistent storage (database)
- Version notes and tags
- Branching and merging
- Version diff visualization
- Automated version creation on query templates



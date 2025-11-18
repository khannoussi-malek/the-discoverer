# Query Result Sharing Documentation

## Overview

Query result sharing allows you to create secure, shareable links for query results. Perfect for sharing insights with team members, stakeholders, or external parties without giving them direct database access.

## Features

- **Secure Links**: Cryptographically secure tokens
- **Expiration**: Set time-based expiration
- **Access Limits**: Limit number of accesses
- **Password Protection**: Optional password protection
- **Email Restrictions**: Restrict access to specific emails
- **Access Tracking**: Monitor share usage

## API Endpoints

### Create Share

```http
POST /api/sharing
Content-Type: application/json

{
  "query_id": "query-123",
  "expires_in_hours": 24,
  "max_accesses": 10,
  "allowed_emails": ["user@example.com"],
  "password": "optional-password"
}
```

**Response:**
```json
{
  "share_id": "share-456",
  "share_token": "abc123...",
  "share_url": "http://localhost:8000/api/shared/abc123...",
  "expires_at": "2024-01-02T12:00:00",
  "max_accesses": 10,
  "created_at": "2024-01-01T12:00:00"
}
```

### Get Shared Result

```http
GET /api/sharing/{share_token}?password=optional-password
```

**Response:**
```json
{
  "query_id": "query-123",
  "share_id": "share-456",
  "result": {
    "merged_data": [...],
    "metadata": {...}
  },
  "created_at": "2024-01-01T12:00:00",
  "access_count": 1
}
```

### List Shares

```http
GET /api/sharing?query_id=query-123
```

**Response:**
```json
{
  "shares": [
    {
      "share_id": "share-456",
      "query_id": "query-123",
      "share_token": "abc123...",
      "expires_at": "2024-01-02T12:00:00",
      "access_count": 5,
      "max_accesses": 10,
      "is_active": true,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total": 1
}
```

### Revoke Share

```http
POST /api/sharing/{share_id}/revoke
```

**Response:**
```json
{
  "message": "Share revoked"
}
```

### Delete Share

```http
DELETE /api/sharing/{share_id}
```

**Response:**
```json
{
  "message": "Share deleted"
}
```

## Examples

### Create a Time-Limited Share

```bash
curl -X POST "http://localhost:8000/api/sharing" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "query-123",
    "expires_in_hours": 24,
    "max_accesses": 5
  }'
```

### Create a Password-Protected Share

```bash
curl -X POST "http://localhost:8000/api/sharing" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "query-123",
    "password": "secret123",
    "expires_in_hours": 48
  }'
```

### Access Shared Result

```bash
# Without password
curl "http://localhost:8000/api/sharing/abc123..."

# With password
curl "http://localhost:8000/api/sharing/abc123...?password=secret123"
```

### Revoke a Share

```bash
curl -X POST "http://localhost:8000/api/sharing/share-456/revoke"
```

## Use Cases

1. **Team Collaboration**: Share query results with team members
2. **Stakeholder Reports**: Share insights with non-technical stakeholders
3. **External Sharing**: Share data with external partners (with expiration)
4. **Temporary Access**: Provide time-limited access to query results
5. **Secure Sharing**: Password-protected shares for sensitive data

## Security Features

1. **Secure Tokens**: Cryptographically secure random tokens
2. **Expiration**: Automatic expiration after set time
3. **Access Limits**: Prevent unlimited access
4. **Password Protection**: Optional password requirement
5. **Email Restrictions**: Limit access to specific emails
6. **Revocation**: Instantly revoke access

## Best Practices

1. **Set Expiration**: Always set expiration for shares
2. **Use Access Limits**: Limit number of accesses
3. **Password Protection**: Use passwords for sensitive data
4. **Monitor Usage**: Regularly check access counts
5. **Revoke Unused**: Revoke shares that are no longer needed
6. **Email Restrictions**: Use email restrictions when possible

## Integration

### Python SDK

```python
from discoverer import DiscovererClient

client = DiscovererClient("http://localhost:8000")

# Create share
share = await client.create_share(
    query_id="query-123",
    expires_in_hours=24,
    max_accesses=10
)

# Get shared result
result = await client.get_shared_result(share["share_token"])
```

### JavaScript SDK

```javascript
import { DiscovererClient } from '@discoverer/sdk';

const client = new DiscovererClient('http://localhost:8000');

// Create share
const share = await client.createShare({
  query_id: 'query-123',
  expires_in_hours: 24,
  max_accesses: 10
});

// Get shared result
const result = await client.getSharedResult(share.share_token);
```



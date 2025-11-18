# Webhooks Documentation

## Overview

Webhooks allow you to receive real-time notifications when events occur in The Discoverer. Perfect for integrating with external systems, monitoring, and automation.

## Features

- **Event Types**: Multiple event types (query.completed, database.registered, etc.)
- **Secure**: HMAC signature verification
- **Reliable**: Success/failure tracking
- **Flexible**: Custom headers and timeouts
- **Testable**: Test webhooks before going live

## Supported Events

- `query.completed` - Query execution completed successfully
- `query.failed` - Query execution failed
- `database.registered` - New database registered
- `database.synced` - Database schema synchronized
- `schema.changed` - Database schema changed
- `dashboard.created` - Dashboard created
- `dashboard.updated` - Dashboard updated
- `export.completed` - Data export completed

## API Endpoints

### Create Webhook

```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["query.completed", "query.failed"],
  "headers": {
    "Authorization": "Bearer token123"
  },
  "timeout": 30
}
```

**Response:**
```json
{
  "id": "webhook-123",
  "url": "https://example.com/webhook",
  "events": ["query.completed", "query.failed"],
  "secret": "abc123...",
  "active": true,
  "created_at": "2024-01-01T12:00:00"
}
```

### List Webhooks

```http
GET /api/webhooks?event=query.completed&active_only=true
```

### Get Webhook

```http
GET /api/webhooks/{webhook_id}
```

### Get Webhook Statistics

```http
GET /api/webhooks/{webhook_id}/stats
```

**Response:**
```json
{
  "webhook_id": "webhook-123",
  "url": "https://example.com/webhook",
  "active": true,
  "events": ["query.completed"],
  "success_count": 150,
  "failure_count": 2,
  "total_count": 152,
  "success_rate": 0.987,
  "last_triggered": "2024-01-01T12:00:00",
  "created_at": "2024-01-01T10:00:00"
}
```

### Update Webhook

```http
PUT /api/webhooks/{webhook_id}
Content-Type: application/json

{
  "events": ["query.completed", "database.registered"],
  "active": true
}
```

### Delete Webhook

```http
DELETE /api/webhooks/{webhook_id}
```

### Test Webhook

```http
POST /api/webhooks/{webhook_id}/test
Content-Type: application/json

{
  "test": true,
  "message": "Test webhook"
}
```

## Webhook Payload

All webhooks send a JSON payload with the following structure:

```json
{
  "event": "query.completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "query_id": "query-123",
    "query": "Show me all users",
    "total_rows": 150,
    "execution_time": 0.5,
    "databases_queried": ["db-1"]
  }
}
```

## Signature Verification

Each webhook includes an HMAC SHA-256 signature in the `X-Webhook-Signature` header. Verify it using your webhook secret:

```python
import hmac
import hashlib

def verify_signature(secret, payload, signature):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Examples

### Create a Webhook

```bash
curl -X POST "http://localhost:8000/api/webhooks" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["query.completed"],
    "headers": {
      "Authorization": "Bearer token123"
    }
  }'
```

### Verify Webhook Signature (Python)

```python
from flask import request
import hmac
import hashlib

@app.route('/webhook', methods=['POST'])
def webhook():
    secret = "your-webhook-secret"
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.get_data(as_text=True)
    
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected, signature):
        return "Invalid signature", 401
    
    data = request.json
    # Process webhook
    return "OK", 200
```

### Verify Webhook Signature (Node.js)

```javascript
const crypto = require('crypto');

function verifySignature(secret, payload, signature) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signature)
  );
}

app.post('/webhook', (req, res) => {
  const secret = 'your-webhook-secret';
  const signature = req.headers['x-webhook-signature'];
  const payload = JSON.stringify(req.body);
  
  if (!verifySignature(secret, payload, signature)) {
    return res.status(401).send('Invalid signature');
  }
  
  // Process webhook
  res.send('OK');
});
```

## Best Practices

1. **Verify Signatures**: Always verify webhook signatures
2. **Use HTTPS**: Only use HTTPS URLs for webhooks
3. **Handle Failures**: Implement retry logic for failed webhooks
4. **Monitor Stats**: Regularly check webhook statistics
5. **Test First**: Use the test endpoint before going live
6. **Set Timeouts**: Configure appropriate timeouts
7. **Filter Events**: Only subscribe to events you need

## Security

- **HMAC Signatures**: All webhooks include HMAC SHA-256 signatures
- **Secret Management**: Store webhook secrets securely
- **HTTPS Only**: Use HTTPS URLs for webhooks
- **Signature Verification**: Always verify signatures before processing

## Integration Examples

### Slack Integration

```python
# Create webhook for Slack
webhook = {
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "events": ["query.completed", "query.failed"],
    "headers": {
        "Content-Type": "application/json"
    }
}
```

### Zapier Integration

```python
# Create webhook for Zapier
webhook = {
    "url": "https://hooks.zapier.com/hooks/catch/YOUR/WEBHOOK/URL",
    "events": ["query.completed"],
    "headers": {}
}
```

### Custom Integration

```python
# Create webhook for custom service
webhook = {
    "url": "https://api.example.com/webhooks/discoverer",
    "events": ["query.completed", "database.registered"],
    "headers": {
        "Authorization": "Bearer your-api-token",
        "X-Custom-Header": "value"
    },
    "timeout": 30
}
```



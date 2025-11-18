# WebSocket API Documentation

## Overview

The Discoverer provides WebSocket support for real-time updates and notifications. This enables:
- Real-time query progress updates
- Live query result notifications
- System status updates
- Interactive query execution

## WebSocket Endpoints

### Query Updates

Subscribe to updates for a specific query:

```
ws://localhost:8000/api/ws/query/{query_id}
```

**Connection Flow:**
1. Connect to WebSocket endpoint
2. Receive connection confirmation
3. Receive query updates as they happen
4. Send ping messages to keep connection alive

**Message Types:**

**From Server:**
- `connected` - Connection established
- `query_update` - Query execution update
- `pong` - Response to ping
- `error` - Error message

**To Server:**
- `ping` - Keep-alive message

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/query/abc123');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
        case 'connected':
            console.log('Connected:', message.message);
            break;
        case 'query_update':
            console.log('Query update:', message.data);
            break;
        case 'pong':
            console.log('Pong received');
            break;
    }
};

// Send ping every 30 seconds
setInterval(() => {
    ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

### General Updates

Subscribe to general system updates:

```
ws://localhost:8000/api/ws/general
```

**Use Cases:**
- System status changes
- Database health updates
- Scheduled query notifications
- General announcements

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/general');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Update:', message);
};
```

## Message Format

All messages are JSON objects:

```json
{
    "type": "message_type",
    "data": { ... },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Query Update Messages

When a query completes, subscribers receive:

```json
{
    "type": "query_update",
    "query_id": "abc123",
    "data": {
        "status": "completed",
        "total_rows": 1000,
        "page": 1,
        "page_size": 20
    }
}
```

## Connection Management

- **Auto-reconnect**: Clients should implement reconnection logic
- **Heartbeat**: Send ping messages every 30 seconds
- **Clean Disconnect**: Close connections properly
- **Connection Limits**: Multiple connections per query are supported

## Best Practices

1. **Error Handling**: Always handle connection errors and reconnection
2. **Heartbeat**: Send ping messages to keep connection alive
3. **Message Validation**: Validate all received messages
4. **Resource Cleanup**: Close connections when no longer needed
5. **Backoff Strategy**: Use exponential backoff for reconnection

## Example Client Implementation

```python
import asyncio
import websockets
import json

async def subscribe_to_query(query_id: str):
    uri = f"ws://localhost:8000/api/ws/query/{query_id}"
    
    async with websockets.connect(uri) as websocket:
        # Send ping every 30 seconds
        async def ping():
            while True:
                await websocket.send(json.dumps({"type": "ping"}))
                await asyncio.sleep(30)
        
        # Start ping task
        ping_task = asyncio.create_task(ping())
        
        try:
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                print(f"Received: {data}")
        finally:
            ping_task.cancel()

# Usage
asyncio.run(subscribe_to_query("abc123"))
```

## Limitations

- Maximum connections: Limited by server resources
- Message size: Keep messages under 1MB
- Connection timeout: 5 minutes of inactivity
- No message persistence: Messages are only sent to active connections

## Future Enhancements

- Message persistence for offline clients
- Authentication for WebSocket connections
- Rate limiting per connection
- Message filtering/subscription topics
- Binary message support



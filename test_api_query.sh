#!/bin/bash
# Simple API test script for Perplexity integration

echo "=========================================="
echo "Testing Perplexity via API"
echo "=========================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Server is not running!"
    echo "   Start it with: make run"
    exit 1
fi

echo "✓ Server is running"
echo ""

# Test query endpoint
echo "Testing query endpoint..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me all users from users table",
    "database_ids": []
  }')

if [ $? -eq 0 ]; then
    echo "✓ API request successful"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "✗ API request failed"
    exit 1
fi


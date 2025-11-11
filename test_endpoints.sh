#!/bin/bash

# Helper function to extract JSON from SSE response
extract_sse_json() {
    grep "^data: " | sed 's/^data: //' | jq '.'
}

echo "=== Testing FastMCP Server Endpoints ==="
echo ""

echo "1. Testing Health Check Endpoint..."
curl -s -X GET http://127.0.0.1:8000/health | jq '.'
echo ""

echo "2. Initializing MCP Session..."
INIT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -D /tmp/headers.txt \
  -d '{
    "jsonrpc": "2.0",
    "id": "init-1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }')

# Extract session ID from headers
SESSION_ID=$(grep -i "mcp-session-id:" /tmp/headers.txt | cut -d' ' -f2 | tr -d '\r\n')
echo "Session ID: $SESSION_ID"
echo "$INIT_RESPONSE" | extract_sse_json
echo ""

echo "3. Sending initialized notification..."
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
echo ""

echo "4. Listing Available Tools..."
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | extract_sse_json
echo ""

echo "5. Calling get_schema tool..."
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_schema",
      "arguments": {}
    }
  }' | extract_sse_json
echo ""

echo "6. Querying listings (postcode: DY4 7LG, max 2 results)..."
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "query_listings",
      "arguments": {
        "postcode": "DY4 7LG",
        "limit": 2
      }
    }
  }' | extract_sse_json
echo ""

echo "7. Calculating average price (postcode: DY4 7LG)..."
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "calculate_average_price",
      "arguments": {
        "postcode": "DY4 7LG"
      }
    }
  }' | extract_sse_json
echo ""

echo "=== All Tests Complete ==="
echo "Session ID used: $SESSION_ID"

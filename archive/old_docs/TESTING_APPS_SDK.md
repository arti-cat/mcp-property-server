# Testing Apps SDK Widget Integration

## The Core Problem

**Neither FastMCP nor the official MCP Python SDK fully support the OpenAI Apps SDK widget format out of the box.**

The Apps SDK requires:
1. Resources with `_meta` fields in the response
2. Tool responses with `{content, structuredContent, _meta}` structure
3. Proper MCP protocol wrapping

## Current Situation

### FastMCP (`server.py`)
- ✅ Easy to use
- ✅ Supports `meta` parameter in `@mcp.resource`
- ❌ May not properly format Apps SDK responses
- ❌ Unknown if `_meta` fields are preserved in tool responses

### Official MCP SDK (`server_mcp_sdk.py`)
- ✅ Official implementation
- ❌ No direct support for `structuredContent` in return types
- ❌ Resource `_meta` not exposed in API
- ❌ More complex to use

## Recommended Approach: Hybrid Solution

Use **FastMCP for tools** + **separate endpoint for widget HTML**:

### Step 1: Keep FastMCP Server

Use `server.py` as-is for the MCP protocol and tools.

### Step 2: Serve Widget HTML Separately

Add a FastAPI endpoint to serve the widget HTML with proper headers:

```python
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# Add to server.py after mcp initialization
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatgpt.com"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/widget/property-list.html")
async def serve_widget():
    """Serve the widget HTML with Apps SDK metadata."""
    html_content = (
        "<div id=\"root\"></div>\n"
        + (f"<script type=\"module\">{PROPERTY_WIDGET_JS}</script>" if PROPERTY_WIDGET_JS else "")
    )
    
    return Response(
        content=html_content,
        media_type="text/html+skybridge",
        headers={
            "X-Widget-Description": "Interactive property listing grid",
            "X-Widget-Prefers-Border": "true",
            "X-Widget-Domain": "https://chatgpt.com"
        }
    )

# Mount FastAPI app alongside FastMCP
# This requires custom server setup
```

### Step 3: Update Tool Annotation

Point to the external widget URL:

```python
@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openai/outputTemplate": "https://your-ngrok-url.ngrok.io/widget/property-list.html",
        "openai/widgetAccessible": True,
    },
)
def query_listings(...):
    ...
```

## Alternative: Wait for Framework Support

Check if newer versions support Apps SDK:

```bash
# Update FastMCP
pip install --upgrade fastmcp

# Check changelog
pip show fastmcp

# Look for Apps SDK or widget support
```

## Testing Steps

### 1. Test Current FastMCP Implementation

```bash
# Start server
python3 server.py --http

# Check if running
curl http://localhost:8000/health

# Start ngrok
ngrok http 8000

# Test in ChatGPT
# 1. Create new connector with ngrok URL
# 2. Start NEW chat
# 3. Enable connector
# 4. Ask: "Show me properties in DY4 under £100,000"
# 5. Check if widget renders or just text
```

### 2. If Widget Doesn't Render

The issue is likely that FastMCP doesn't properly format the Apps SDK response.

**Evidence to look for:**
- Tool is called ✅
- Data is returned ✅
- But widget doesn't render ❌
- Only text output shown ❌

**This confirms:** FastMCP doesn't support Apps SDK format.

### 3. Next Steps if FastMCP Doesn't Work

**Option A: Hybrid Approach** (Recommended)
- Keep FastMCP for tools
- Serve widget HTML via separate endpoint
- Update `openai/outputTemplate` to external URL

**Option B: Use TypeScript SDK**
- OpenAI's examples use TypeScript
- Better Apps SDK support
- Requires rewriting server

**Option C: Report Issue**
- Open issue on FastMCP GitHub
- Request Apps SDK support
- Wait for update

## Quick Test Script

Save as `test_widget.sh`:

```bash
#!/bin/bash

echo "Testing Property MCP Server with Apps SDK..."

# 1. Check server is running
echo "1. Checking server health..."
curl -s http://localhost:8000/health | jq .

# 2. Check if widget bundle exists
echo "2. Checking widget bundle..."
ls -lh web/dist/component.js

# 3. Check ngrok tunnel
echo "3. Checking ngrok tunnel..."
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'

echo ""
echo "Next steps:"
echo "1. Go to ChatGPT"
echo "2. Start a NEW chat (important!)"
echo "3. Enable your connector"
echo "4. Ask: 'Show me properties in DY4 under £100,000'"
echo "5. Check if widget renders or just text"
```

## Expected Outcomes

### If Widget Renders ✅
- You see property cards
- Favorites work
- Sort works
- **Conclusion:** FastMCP supports Apps SDK!

### If Only Text Shows ❌
- Tool is called
- Data is returned
- But no widget UI
- **Conclusion:** FastMCP doesn't support Apps SDK format
- **Action:** Use hybrid approach or TypeScript SDK

## References

- FastMCP Docs: https://gofastmcp.com
- OpenAI Apps SDK: https://developers.openai.com/apps-sdk/
- Apps SDK Examples (TypeScript): https://github.com/openai/openai-apps-sdk-examples
- MCP Protocol: https://modelcontextprotocol.io/

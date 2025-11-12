# Apps SDK Implementation - Property MCP Server

## Goal

Build an OpenAI Apps SDK integration with custom React widgets for property listings.

## Current Status

✅ Widget built (React component - 149KB)
✅ MCP server with tools
❌ Widget not rendering in ChatGPT

## The Challenge

Apps SDK requires specific response formats that standard MCP libraries may not fully support.

## Solution: Hybrid Approach

Use **official MCP SDK** for protocol + **FastAPI** for widget serving.

## Implementation

### File: `server_apps_sdk.py`

This server combines:
1. **MCP SDK** - For tool protocol
2. **FastAPI** - For widget HTML serving
3. **SSE Transport** - For ChatGPT connection

### Key Features

1. **Widget HTML Endpoint**
   ```
   GET /widget/property-list.html
   ```
   - Serves React widget with proper MIME type
   - CORS headers for ChatGPT
   - Apps SDK metadata in headers

2. **MCP Tools with Apps SDK Annotations**
   ```python
   annotations={
       "openai/outputTemplate": "ui://widget/property-list.html",
       "openai/widgetAccessible": True,
       "openai/toolInvocation/invoking": "Searching...",
       "openai/toolInvocation/invoked": "Found properties"
   }
   ```

3. **Structured Content in Tool Responses**
   ```python
   {
       "content": [...],
       "structuredContent": {...},
       "_meta": {}
   }
   ```

## How to Use

### 1. Build Widget

```bash
cd web
npm install
npm run build
```

Verify: `ls -lh dist/component.js` (should be ~149KB)

### 2. Start Server

```bash
python3 server_apps_sdk.py
```

You should see:
```
======================================================================
Property MCP Server - OpenAI Apps SDK
======================================================================
Mode: Apps SDK with Custom Widgets
Port: 8000

Endpoints:
  MCP SSE:      http://127.0.0.1:8000/mcp/sse
  MCP Messages: http://127.0.0.1:8000/mcp/messages
  Health:       http://127.0.0.1:8000/health
  Widget HTML:  http://127.0.0.1:8000/widget/property-list.html

Widget Status:
  ✅ Loaded (152,xxx bytes)
======================================================================
```

### 3. Test Widget Endpoint

```bash
curl http://localhost:8000/widget/property-list.html
```

Should return HTML with embedded JavaScript.

### 4. Expose with ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 5. Connect to ChatGPT

1. **Enable Developer Mode**
   - Settings → Connectors → Advanced → Developer Mode

2. **Create Connector**
   - Name: Property Server
   - URL: `https://your-ngrok-url.ngrok.io/mcp/`
   - Trust provider ✓

3. **Test in NEW Chat**
   - Enable connector
   - Ask: "Show me properties in DY4 under £100,000"

## Expected Behavior

### If Widget Works ✅
- Property cards render
- Favorites work
- Sort works
- Interactive UI

### If Widget Doesn't Work ❌
- Tool is called ✓
- Data is returned ✓
- But only text shows

**If this happens**, the issue is likely:
1. ChatGPT's Apps SDK implementation
2. Widget URL not being fetched
3. MIME type not recognized

## Debugging

### Check Widget Loads

```bash
# Test widget endpoint
curl -I http://localhost:8000/widget/property-list.html

# Should show:
# Content-Type: text/html+skybridge
# X-Widget-Description: ...
```

### Check MCP Connection

```bash
# Test health
curl http://localhost:8000/health

# Should return JSON with widget_loaded: true
```

### Check Tool Response

In ChatGPT, the tool should return structured data. Check the response format.

## Alternative: External Widget URL

If the widget still doesn't render, try referencing an external URL:

### Update Tool Annotation

```python
annotations={
    "openai/outputTemplate": "https://your-ngrok-url.ngrok.io/widget/property-list.html"
}
```

This makes ChatGPT fetch the widget from HTTP instead of MCP Resources.

## Why This Approach

1. **MCP SDK** - Official protocol implementation
2. **FastAPI** - Full control over widget serving
3. **Hybrid** - Best of both worlds

## Comparison with Other Approaches

| Approach | MCP Tools | Widget Serving | Complexity |
|----------|-----------|----------------|------------|
| FastMCP only | ✅ | ❌ (Resources not supported) | Low |
| Official SDK only | ✅ | ⚠️ (Limited) | Medium |
| **Hybrid (This)** | ✅ | ✅ (Full control) | Medium |
| TypeScript SDK | ✅ | ✅ | High (rewrite) |

## Next Steps

### If Widget Renders ✅
1. Test all features (favorites, sort, filters)
2. Add more properties to test pagination
3. Deploy to production

### If Widget Doesn't Render ❌
1. Check browser console (F12) for errors
2. Verify widget URL is accessible
3. Try TypeScript SDK (official OpenAI examples)

## Key Files

- `server_apps_sdk.py` - Apps SDK server
- `web/src/PropertyListWidget.tsx` - React widget
- `web/dist/component.js` - Built bundle
- `tools.py` - Property query logic

## References

- OpenAI Apps SDK: https://developers.openai.com/apps-sdk/
- Apps SDK Examples: https://github.com/openai/openai-apps-sdk-examples
- MCP Specification: https://modelcontextprotocol.io/
- Your docs: `docs/external/mcpoai2.md`, `docs/external/custom-ui.md`

## Success Criteria

✅ Server starts without errors
✅ Widget bundle loads
✅ Health endpoint responds
✅ Widget HTML endpoint serves content
✅ MCP tools work in ChatGPT
🎯 **Widget renders in ChatGPT** ← The goal!

Test it now and let me know if the widget renders!

# Widget Fix Summary - Apps SDK Integration

## Problem

The widget wasn't rendering in ChatGPT even though:
- ✅ Server was running on port 8000
- ✅ ngrok tunnel was active
- ✅ ChatGPT connector was configured
- ✅ Tool was being called successfully
- ✅ Images were showing (proving data was flowing)

## Root Cause

The MCP server was missing the **Apps SDK integration**:
1. No HTML resource registered for the widget
2. No `openai/outputTemplate` annotation linking the tool to the widget
3. No `structuredContent` key in the tool response

## Changes Made

### 1. Added HTML Resource (`server.py`)

Registered a Skybridge HTML resource that inlines the built React bundle:

```python
# Load the built widget bundle
PROPERTY_WIDGET_JS = ""
try:
    with open(os.path.join("web", "dist", "component.js"), "r", encoding="utf-8") as f:
        PROPERTY_WIDGET_JS = f.read()
except FileNotFoundError:
    PROPERTY_WIDGET_JS = ""

# Register the UI template as a Resource
@mcp.resource(
    uri="ui://widget/property-list.html",
    title="Property List Widget",
    mime_type="text/html+skybridge",  # Required for Apps SDK
)
def property_list_widget():
    """HTML template for the property list widget (rendered in ChatGPT)."""
    return (
        "<div id=\"root\"></div>\n"
        + (f"<script type=\"module\">{PROPERTY_WIDGET_JS}</script>" if PROPERTY_WIDGET_JS else "")
    )
```

**Key points:**
- `mime_type="text/html+skybridge"` is **required** for ChatGPT to recognize it as a widget
- `uri="ui://widget/property-list.html"` is the canonical ID for the component
- The HTML inlines the built JavaScript bundle

### 2. Linked Tool to Widget (`server.py`)

Added Apps SDK annotations to the `query_listings` tool:

```python
@mcp.tool(
    annotations={
        "readOnlyHint": True,
        # Link this tool to the UI template
        "openai/outputTemplate": "ui://widget/property-list.html",
        # Allow component-initiated tool calls
        "openai/widgetAccessible": True,
    },
)
def query_listings(...):
    ...
```

**Key points:**
- `openai/outputTemplate` links the tool to the HTML resource URI
- `openai/widgetAccessible` allows the widget to call tools via `window.openai.callTool()`
- These go in `annotations`, NOT `meta` (per FastMCP docs)

### 3. Added structuredContent (`tools.py`)

Modified the tool response to include `structuredContent` for Apps SDK:

```python
payload = {
    "properties": filtered_results[:limit],
    "filters_applied": {...},
    "total_results": len(filtered_results),
    "showing": min(limit, len(filtered_results)),
}

# For Apps SDK, ChatGPT hydrates the component from `structuredContent`
payload["structuredContent"] = {
    "properties": payload["properties"],
    "filters_applied": payload["filters_applied"],
    "total_results": payload["total_results"],
    "showing": payload["showing"],
}

return payload
```

**Key points:**
- `structuredContent` is injected into `window.openai.toolOutput` in the widget
- We keep top-level keys for backwards compatibility with existing tests
- All 13 pytest tests still pass ✅

## How to Test

### 1. Verify Server is Running

```bash
# Check health endpoint
curl http://127.0.0.1:8000/health

# Should return:
# {"status":"healthy","service":"PropertyServer","version":"1.0.0"}
```

### 2. Verify ngrok Tunnel

```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels | python3 -m json.tool | grep public_url

# Should show:
# "public_url": "https://unblemished-kaycee-downily.ngrok-free.dev"
```

### 3. Test in ChatGPT

**Important**: You need to start a **NEW chat** for ChatGPT to pick up the changes!

1. **Start a new chat** (don't reuse the old one)
2. Click **+** → **More** → **Developer Mode**
3. Enable your **Property Server** connector
4. Ask: "Show me properties in DY4 under £100,000"

**Expected behavior:**
- ✅ Tool is called
- ✅ **Widget renders** with property cards
- ✅ Images load
- ✅ Favorite button works
- ✅ Sort dropdown works
- ✅ Dark mode works

### 4. Verify Resource is Registered

You can use MCP Inspector or curl to verify the resource:

```bash
# List resources (requires MCP client)
# The resource should appear as:
# - URI: ui://widget/property-list.html
# - MIME type: text/html+skybridge
```

## Troubleshooting

### Widget Still Not Showing

1. **Start a NEW chat** - ChatGPT caches connector metadata
2. **Check server logs** - Look for errors when loading `component.js`
3. **Verify bundle exists**: `ls -lh web/dist/component.js`
4. **Rebuild if needed**: `cd web && npm run build`
5. **Restart server**: `pkill -f 'python3 server.py' && python3 server.py --http`

### Images Show But No Widget

This means:
- ✅ Tool is being called
- ✅ Data is flowing
- ❌ Widget template not registered or not linked

**Fix:**
- Verify `@mcp.resource` decorator is present
- Verify `openai/outputTemplate` annotation matches resource URI exactly
- Check server logs for resource registration errors

### Widget Shows But Broken

1. **Check browser console** (F12 in ChatGPT)
2. **Look for JavaScript errors**
3. **Verify `window.openai` is available**
4. **Test locally first**: Open `web/test.html` in browser

## Testing Checklist

- [ ] Server running on port 8000
- [ ] ngrok tunnel active
- [ ] Health endpoint returns 200
- [ ] All 13 pytest tests pass
- [ ] Bundle exists at `web/dist/component.js`
- [ ] **Started NEW chat in ChatGPT**
- [ ] Connector enabled in chat
- [ ] Tool called successfully
- [ ] Widget renders with property cards
- [ ] Favorites work
- [ ] Sort works
- [ ] Dark mode works

## Files Modified

1. **`server.py`**
   - Added `import os`
   - Added `PROPERTY_WIDGET_JS` loading
   - Added `@mcp.resource` for widget HTML
   - Added `annotations` to `query_listings` tool

2. **`tools.py`**
   - Added `structuredContent` to response
   - Maintained backwards compatibility

3. **Tests**
   - No changes needed
   - All 13 tests still pass ✅

## Next Steps

1. **Test in ChatGPT** with a new chat
2. **Verify widget renders** correctly
3. **Test all features** (favorites, sort, dark mode)
4. **Gather feedback** from users
5. **Plan v2 features** (load more, filters, etc.)

## References

- [Apps SDK - Set up your server](https://developers.openai.com/apps-sdk/build/mcp-server/)
- [FastMCP - Resources](https://gofastmcp.com/servers/resources)
- [FastMCP - Context](https://gofastmcp.com/servers/context)
- [MCP Protocol](https://modelcontextprotocol.io)

---

**Status**: ✅ Fixed and ready for testing
**Server**: Running on port 8000
**ngrok**: https://unblemished-kaycee-downily.ngrok-free.dev
**Next**: Start a NEW chat in ChatGPT and test!

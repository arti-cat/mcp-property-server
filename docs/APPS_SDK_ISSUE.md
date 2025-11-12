# Apps SDK Widget Not Rendering - Root Cause Analysis

## The Problem

Widget is not rendering in ChatGPT. Tool is called successfully, but ChatGPT shows normal text output instead of the custom React widget.

## Root Cause

**FastMCP may not fully support OpenAI Apps SDK widget format.**

There are **TWO different ChatGPT integration modes**:

### 1. Chat Mode (What FastMCP Supports)
- Simple tool calling
- Text-based responses
- No custom UI widgets
- Documented at: https://gofastmcp.com/integrations/chatgpt

### 2. Apps SDK Mode (What You're Trying to Build)
- Custom React widgets
- Interactive UI components
- Requires specific MCP response format
- Documented at: https://developers.openai.com/apps-sdk/

## The Issue with FastMCP

FastMCP's `@mcp.resource` decorator and `@mcp.tool` may not properly format responses for Apps SDK because:

1. **Resource Format**: Apps SDK requires resources to return:
   ```python
   {
     "contents": [{
       "uri": "ui://widget/...",
       "mimeType": "text/html+skybridge",
       "text": "<html>...",
       "_meta": {
         "openai/widgetDescription": "...",
         "openai/widgetPrefersBorder": true
       }
     }]
   }
   ```

2. **Tool Response Format**: Apps SDK requires tools to return:
   ```python
   {
     "content": [{"type": "text", "text": "..."}],
     "structuredContent": {...},
     "_meta": {...}
   }
   ```

3. **FastMCP Behavior**: FastMCP's decorators may auto-convert responses to standard MCP format, stripping the Apps SDK-specific fields.

## Solutions

### Option 1: Use Official MCP SDK (Recommended)

The official MCP Python SDK properly supports Apps SDK format. See `server_mcp_sdk.py` for an implementation.

**Pros:**
- Full Apps SDK support
- Proper `_meta` field handling
- Official OpenAI documentation applies

**Cons:**
- More verbose than FastMCP
- Requires rewriting server code

### Option 2: Serve Widget HTML Separately

Serve the widget HTML via a separate FastAPI endpoint instead of as an MCP resource.

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/widget/property-list.html")
async def serve_widget():
    # Return the HTML file with proper headers
    return FileResponse(
        "web/dist/component.html",
        media_type="text/html+skybridge",
        headers={
            "Access-Control-Allow-Origin": "https://chatgpt.com",
            "X-Widget-Description": "Property listing widget"
        }
    )
```

Then reference it in the tool annotation:
```python
@mcp.tool(annotations={
    "openai/outputTemplate": "https://your-server.ngrok.io/widget/property-list.html"
})
```

**Pros:**
- Keep using FastMCP for tools
- Full control over widget serving
- Can add custom headers

**Cons:**
- Widget URL must be publicly accessible
- More complex deployment

### Option 3: Wait for FastMCP Apps SDK Support

FastMCP may add Apps SDK support in the future. Check:
- https://github.com/jlowin/fastmcp/issues
- FastMCP documentation updates

## Testing the Issue

To confirm FastMCP is the issue, check the MCP protocol responses:

1. **Start server**: `python3 server.py --http`
2. **Use MCP Inspector**: Point to `http://localhost:8000/mcp`
3. **List resources**: Check if `_meta` fields are present
4. **Call tool**: Check if response includes `structuredContent` and `_meta`

If `_meta` fields are missing or transformed, FastMCP is stripping them.

## Recommended Next Steps

1. **Test with Official SDK**: Try `server_mcp_sdk.py` to see if widget renders
2. **Check FastMCP Version**: Ensure you have latest version (`pip install --upgrade fastmcp`)
3. **Report Issue**: If FastMCP doesn't support Apps SDK, open an issue on GitHub
4. **Use Hybrid Approach**: Use FastMCP for tools, separate endpoint for widget HTML

## References

- FastMCP ChatGPT Integration: https://gofastmcp.com/integrations/chatgpt
- OpenAI Apps SDK: https://developers.openai.com/apps-sdk/
- MCP Protocol Spec: https://modelcontextprotocol.io/
- FastMCP GitHub: https://github.com/jlowin/fastmcp

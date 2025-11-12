# Widget Not Rendering - Diagnosis & Solution

## Problem Summary

Widget is not rendering in ChatGPT. Tool is called successfully, but ChatGPT shows normal text output instead of the custom React widget.

## Root Cause

**FastMCP likely doesn't fully support OpenAI Apps SDK widget format.**

ChatGPT Apps SDK requires a specific response format that FastMCP may not be generating correctly.

## What Apps SDK Needs

### 1. Resource Format
Resources must return with `_meta` fields:
```json
{
  "contents": [{
    "uri": "ui://widget/property-list.html",
    "mimeType": "text/html+skybridge",
    "text": "<html>...",
    "_meta": {
      "openai/widgetDescription": "...",
      "openai/widgetPrefersBorder": true
    }
  }]
}
```

### 2. Tool Response Format
Tools must return:
```json
{
  "content": [{"type": "text", "text": "..."}],
  "structuredContent": {...},
  "_meta": {...}
}
```

### 3. Tool Metadata
Tools must have annotations:
```python
annotations={
    "openai/outputTemplate": "ui://widget/property-list.html",
    "openai/widgetAccessible": True
}
```

## What We Have

✅ Widget bundle built (`web/dist/component.js` - 149KB)
✅ Resource registered with `@mcp.resource`
✅ Tool has correct annotations
✅ Tool returns `{content, structuredContent, _meta}` format
❌ **FastMCP may not preserve this format in MCP protocol response**

## The Issue

FastMCP is designed for **Chat Mode** (simple tool calling), not **Apps SDK** (custom widgets).

From FastMCP docs: https://gofastmcp.com/integrations/chatgpt
- Only mentions Chat Mode and Deep Research Mode
- No mention of Apps SDK or custom widgets
- No examples of `structuredContent` or widget rendering

## Recommended Solutions

### Option 1: Use TypeScript SDK (Easiest)

OpenAI's Apps SDK examples are all in TypeScript. This is the officially supported path.

**Pros:**
- Official support
- All examples work
- Full Apps SDK features

**Cons:**
- Requires rewriting server in TypeScript
- More setup than Python

**Resources:**
- https://github.com/openai/openai-apps-sdk-examples
- https://developers.openai.com/apps-sdk/

### Option 2: Hybrid Approach (Keep Python)

Keep FastMCP for tools, serve widget HTML separately.

**Implementation:**
1. Keep `server.py` for MCP tools
2. Add FastAPI endpoint for widget HTML
3. Update `openai/outputTemplate` to external URL

**Example:**
```python
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.get("/widget/property-list.html")
async def serve_widget():
    return Response(
        content=PROPERTY_WIDGET_JS,
        media_type="text/html+skybridge",
        headers={"Access-Control-Allow-Origin": "https://chatgpt.com"}
    )

# Then in tool annotation:
annotations={
    "openai/outputTemplate": "https://your-server.com/widget/property-list.html"
}
```

**Pros:**
- Keep Python
- Keep FastMCP for tools
- Full control over widget serving

**Cons:**
- More complex setup
- Need to manage two endpoints

### Option 3: Wait/Request FastMCP Support

Check if FastMCP will add Apps SDK support.

**Actions:**
1. Check FastMCP GitHub issues
2. Open feature request if not exists
3. Monitor for updates

**Pros:**
- Eventually get full Python support
- Keep simple FastMCP API

**Cons:**
- Unknown timeline
- May never be added

## Testing Current Implementation

To confirm FastMCP is the issue:

```bash
# 1. Ensure server is running
python3 server.py --http

# 2. Ensure ngrok is running
ngrok http 8000

# 3. In ChatGPT:
#    - Start NEW chat
#    - Enable connector
#    - Ask: "Show me properties in DY4 under £100,000"

# 4. Observe:
#    - Tool is called ✅
#    - Data is returned ✅
#    - Widget renders? ❌ (likely)
#    - Only text shown? ✅ (likely)

# This confirms: FastMCP doesn't support Apps SDK format
```

## Next Steps

### Immediate (Test Current Setup)
1. Test in ChatGPT with NEW chat
2. Confirm widget doesn't render
3. Document exact behavior

### Short Term (Get Widget Working)
Choose one:
- **Option A**: Rewrite in TypeScript (official path)
- **Option B**: Hybrid approach (keep Python)

### Long Term (Python Support)
- Monitor FastMCP for Apps SDK support
- Consider contributing to FastMCP
- Or maintain hybrid solution

## Key Insight

**FastMCP Chat Mode ≠ Apps SDK**

- **Chat Mode**: Simple tool calling, text responses
- **Apps SDK**: Custom widgets, interactive UI

FastMCP supports Chat Mode. Apps SDK needs different approach.

## References

- FastMCP ChatGPT Integration: https://gofastmcp.com/integrations/chatgpt
- OpenAI Apps SDK: https://developers.openai.com/apps-sdk/
- Apps SDK Examples (TypeScript): https://github.com/openai/openai-apps-sdk-examples
- MCP Protocol: https://modelcontextprotocol.io/

## Conclusion

Your implementation is **correct per Apps SDK spec**, but FastMCP likely doesn't support the required format.

**Recommendation**: Try the hybrid approach first (Option 2) to keep Python, or switch to TypeScript for official support (Option 1).

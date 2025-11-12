# ChatGPT MCP Reality - What Actually Works

## Critical Finding from MCP Specification

After reviewing the official MCP specification at https://modelcontextprotocol.io/llms-full.txt, here's what ChatGPT **actually supports**:

### ChatGPT MCP Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **Tools** | ✅ Yes | Full support |
| **Resources** | ❌ No | Not supported |
| **Prompts** | ❌ No | Not supported |
| **Discovery** | ❌ No | Not supported |
| **Sampling** | ❌ No | Not supported |
| **Roots** | ❌ No | Not supported |
| **Elicitation** | ❌ No | Not supported |
| **Instructions** | ❓ Unknown | Not documented |

**Source**: MCP Specification - Example Clients Feature Matrix

## What This Means

### 1. ChatGPT Only Supports Tools

ChatGPT's MCP implementation is **tools-only**. This means:

- ✅ You can call tools (functions)
- ❌ You cannot use MCP Resources (including widget HTML)
- ❌ You cannot use MCP Prompts
- ❌ You cannot use other MCP features

### 2. Widget Support is Separate from MCP

The **Apps SDK widget functionality** is NOT part of standard MCP. It's a separate OpenAI feature that:

- Uses MCP for tool calling
- Uses separate mechanisms for widget rendering
- May not be fully supported in Chat Mode (only in Apps SDK mode)

### 3. Two Different Integration Paths

**Path A: Chat Mode (MCP Tools Only)**
- What we've been using
- Only tool calling
- Text/JSON responses
- No custom widgets
- Works with FastMCP

**Path B: Apps SDK (Custom Widgets)**
- Separate from standard MCP
- Requires specific OpenAI APIs
- Custom React widgets
- May not work with standard MCP servers
- Requires TypeScript SDK or special setup

## Why Your Widget Isn't Rendering

Based on the MCP specification review:

1. **ChatGPT doesn't support MCP Resources**
   - Your `@mcp.resource` for widget HTML won't work
   - ChatGPT can't fetch resources via MCP protocol

2. **Apps SDK is not standard MCP**
   - Apps SDK widgets use proprietary OpenAI mechanisms
   - Standard MCP servers (FastMCP, official SDK) don't automatically support it

3. **You're mixing two different systems**
   - MCP (for tools) ✅
   - Apps SDK (for widgets) ❌

## The Solution

### Option 1: Chat Mode Only (Simplest)

Accept that ChatGPT Chat Mode = text responses only.

**What works:**
- All 3 tools work perfectly
- Data is returned correctly
- Users can query properties

**What doesn't work:**
- Custom widgets
- Interactive UI

**Implementation:**
- Use `server_chatgpt_compatible.py`
- No changes needed
- Already working!

### Option 2: Apps SDK with Separate Widget Endpoint

Serve widget HTML via HTTP, not MCP Resources.

**Implementation:**

1. **Keep MCP for tools** (already working)

2. **Serve widget via HTTP endpoint:**
   ```python
   @mcp.custom_route("/widget/property-list.html", methods=["GET"])
   async def serve_widget(request):
       return Response(
           content=widget_html,
           media_type="text/html",
           headers={"Access-Control-Allow-Origin": "https://chatgpt.com"}
       )
   ```

3. **Reference external URL in tool response:**
   ```python
   return {
       "content": [...],
       "structuredContent": {...},
       "_meta": {
           "openai/widgetUrl": "https://your-server.com/widget/property-list.html"
       }
   }
   ```

**Pros:**
- Keep Python
- Keep FastMCP
- Potentially get widgets working

**Cons:**
- Experimental
- May not work (Apps SDK support unclear)
- More complex

### Option 3: TypeScript SDK with Full Apps SDK

Use OpenAI's official TypeScript examples.

**Pros:**
- Official support
- All examples work
- Full Apps SDK features

**Cons:**
- Rewrite in TypeScript
- More setup

## Recommended Approach

### For Production: Option 1 (Chat Mode Only)

**Why:**
- Already working
- Simple and reliable
- ChatGPT's MCP support is tools-only anyway
- Users can still query all property data

**Implementation:**
```bash
# Use the ChatGPT-compatible server
python3 server_chatgpt_compatible.py --http

# Expose with ngrok
ngrok http 8000

# Connect to ChatGPT
# Works perfectly for tool calling
```

### For Experimentation: Option 2 (Hybrid)

Try serving widget HTML separately to see if Apps SDK picks it up.

**Steps:**
1. Use `server_chatgpt_compatible.py` (already has widget endpoint)
2. Test if ChatGPT can load widget from HTTP endpoint
3. If it works, great! If not, fall back to Option 1

## Key Insights

### 1. MCP ≠ Apps SDK

- **MCP**: Protocol for tool calling (what ChatGPT supports)
- **Apps SDK**: OpenAI's widget framework (separate system)

### 2. ChatGPT's MCP is Limited

From the specification:
- Only tools supported
- No resources, prompts, or other features
- This is by design, not a bug

### 3. Your Implementation is Correct

Your FastMCP server is **correct for MCP**. The issue is:
- ChatGPT's MCP doesn't support resources
- Apps SDK widgets need different approach

## Testing the ChatGPT-Compatible Server

```bash
# 1. Start server
python3 server_chatgpt_compatible.py --http

# 2. Check health
curl http://localhost:8000/health

# 3. Check widget endpoint (experimental)
curl http://localhost:8000/widget/property-list.html

# 4. Start ngrok
ngrok http 8000

# 5. Connect to ChatGPT
# Use ngrok URL in connector

# 6. Test in ChatGPT
# Ask: "Show me properties in DY4 under £100,000"
# Should work perfectly for tool calling
```

## Conclusion

**Your MCP server works correctly.** The issue is:

1. ChatGPT only supports MCP tools (per specification)
2. Widgets require Apps SDK, which is separate from MCP
3. Standard MCP servers don't automatically support Apps SDK

**Recommendation**: Use Chat Mode (Option 1) for reliable, working integration. The tools work perfectly, users get all the data they need, just without custom widgets.

If you really need widgets, you'll likely need to:
- Use OpenAI's TypeScript SDK
- Follow their Apps SDK examples exactly
- Accept that it's a separate system from standard MCP

## References

- MCP Specification: https://modelcontextprotocol.io/llms-full.txt
- ChatGPT Feature Matrix: Shows tools-only support
- OpenAI Apps SDK: https://developers.openai.com/apps-sdk/
- FastMCP Docs: https://gofastmcp.com/integrations/chatgpt

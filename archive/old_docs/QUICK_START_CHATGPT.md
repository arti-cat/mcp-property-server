# Quick Start: Property MCP Server for ChatGPT

## TL;DR

ChatGPT only supports **MCP Tools** (not Resources/Widgets). Your server works perfectly for tool calling. Custom widgets require a different approach.

## Start the Server

```bash
# Use the ChatGPT-compatible server
python3 server_chatgpt_compatible.py --http
```

You should see:
```
======================================================================
Starting Property MCP Server (ChatGPT Compatible)
======================================================================
Transport: HTTP
Port: 8000
MCP Endpoint: http://127.0.0.1:8000/mcp
Health Check: http://127.0.0.1:8000/health
Widget HTML: http://127.0.0.1:8000/widget/property-list.html

ChatGPT MCP Support:
  ✅ Tools: Supported
  ❌ Resources: Not supported by ChatGPT
  ❌ Prompts: Not supported by ChatGPT
  ❌ Sampling: Not supported by ChatGPT

For Apps SDK widgets, use the widget HTML endpoint above.
======================================================================
```

## Expose with ngrok

```bash
# In a separate terminal
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

## Connect to ChatGPT

### 1. Enable Developer Mode

1. Open ChatGPT → **Settings** → **Connectors**
2. Under **Advanced**, toggle **Developer Mode** to **enabled**

### 2. Create Connector

1. In **Settings** → **Connectors**, click **Create**
2. Enter:
   - **Name**: Property Server
   - **Server URL**: `https://your-ngrok-url.ngrok.io/mcp/`
   - Check **I trust this provider**
3. Click **Create**

### 3. Use in Chat

1. Start a **NEW chat** (important!)
2. Click **+** → **More** → **Developer Mode**
3. **Enable your Property Server connector**
4. Ask questions:
   - "Show me properties in DY4 under £100,000"
   - "Find flats with parking"
   - "What's the average price in LE65?"

## What Works

✅ **All 3 tools work perfectly:**
- `get_schema()` - Returns data schema
- `query_listings()` - Search and filter properties
- `calculate_average_price()` - Calculate averages

✅ **Data is returned correctly:**
- 475 property listings
- Filtering by postcode, price, bedrooms, etc.
- JSON responses with all property details

✅ **Read-only hints:**
- No confirmation prompts
- Smooth conversation flow

## What Doesn't Work (and Why)

❌ **Custom React widgets**
- **Reason**: ChatGPT's MCP only supports tools, not resources
- **Per MCP Spec**: ChatGPT feature matrix shows tools-only support
- **Solution**: Accept text/JSON responses, or use Apps SDK separately

## Understanding the Limitation

From the official MCP specification:

**ChatGPT MCP Support:**
- Tools: ✅ Supported
- Resources: ❌ Not supported
- Prompts: ❌ Not supported
- Everything else: ❌ Not supported

This means:
- MCP Resources (widget HTML) won't work
- Apps SDK widgets need different approach
- Your server is correct; ChatGPT's MCP is limited

## Example Queries

Try these in ChatGPT:

```
Show me all properties in DY4 7LG

Find flats under £100,000 with parking

What's the average price for 2-bedroom properties?

Show me properties with gardens in Ashby

Get the data schema for properties
```

## Troubleshooting

### Tools Not Showing Up

1. **Start a NEW chat** - ChatGPT caches connector metadata
2. **Enable connector** - Must be explicitly enabled in each chat
3. **Check server** - Ensure it's running and ngrok is active

### Server Not Responding

```bash
# Check health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"PropertyServer",...}
```

### ngrok Issues

```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels | python3 -m json.tool

# Should show public_url
```

## Files

- `server_chatgpt_compatible.py` - ChatGPT-optimized server
- `docs/CHATGPT_MCP_REALITY.md` - Full explanation
- `docs/APPS_SDK_ISSUE.md` - Widget integration details

## Next Steps

### For Production

Use this setup! It works perfectly for ChatGPT's actual MCP capabilities.

### For Widgets

If you need custom widgets:
1. **Option A**: Use OpenAI's TypeScript SDK with Apps SDK
2. **Option B**: Serve widget HTML separately (experimental)
3. **Option C**: Accept text/JSON responses (recommended)

## Key Takeaway

**Your server works correctly.** ChatGPT's MCP support is tools-only (per specification). Custom widgets require Apps SDK, which is separate from standard MCP.

For most use cases, tool calling with JSON responses is sufficient and works great!

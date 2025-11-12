# Apps SDK Deployment Guide

## ✅ Pre-flight Checklist

- [x] Widget built (149KB at `web/dist/component.js`)
- [x] React component uses `window.openai` API correctly
- [x] Hooks implement `useOpenAiGlobal`, `useToolOutput`, `useWidgetState`
- [x] Server implements Apps SDK format
- [ ] Test deployment

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         ChatGPT                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  User asks: "Show me properties in DY4"            │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  MCP Client calls: query_listings(postcode="DY4")  │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SSE/HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Your MCP Server                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Tool: query_listings                               │     │
│  │  Returns: {                                         │     │
│  │    content: [...],                                  │     │
│  │    structuredContent: {properties: [...], ...},     │     │
│  │    _meta: {}                                        │     │
│  │  }                                                  │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Widget HTML Endpoint                               │     │
│  │  /widget/property-list.html                         │     │
│  │  Returns: HTML + embedded React bundle              │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Loads widget
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Widget (iframe)                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  React Component                                    │     │
│  │  - Reads: window.openai.toolOutput                  │     │
│  │  - Displays: Property cards with favorites          │     │
│  │  - Persists: window.openai.setWidgetState()         │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Start the Apps SDK Server

```bash
python3 server_apps_sdk.py
```

**Expected output:**
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
  ✅ Loaded (152,576 bytes)
======================================================================
```

## Step 2: Test Locally

### Test Health Endpoint
```bash
curl http://localhost:8000/health | python3 -m json.tool
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "PropertyServer",
  "version": "3.0.0-apps-sdk",
  "mode": "OpenAI Apps SDK",
  "widget_loaded": true,
  "widget_size": 152576
}
```

### Test Widget HTML
```bash
curl http://localhost:8000/widget/property-list.html | head -20
```

**Expected:** HTML with embedded JavaScript

### Test CORS Headers
```bash
curl -I http://localhost:8000/widget/property-list.html
```

**Expected headers:**
```
Content-Type: text/html+skybridge
X-Widget-Description: Interactive property listing grid...
X-Widget-Prefers-Border: true
Access-Control-Allow-Origin: https://chatgpt.com
```

## Step 3: Expose with ngrok

```bash
ngrok http 8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

## Step 4: Connect to ChatGPT

### Enable Developer Mode

1. Open ChatGPT
2. Go to **Settings** → **Connectors**
3. Under **Advanced**, enable **Developer Mode**

### Create MCP Connector

1. In **Settings** → **Connectors**, click **Create**
2. Fill in:
   - **Name**: `Property Server`
   - **Server URL**: `https://your-ngrok-url.ngrok-free.app/mcp/`
   - Check **I trust this provider**
3. Click **Create**

**Important:** The URL must end with `/mcp/` (with trailing slash)

## Step 5: Test in ChatGPT

### Start a NEW Chat

**Critical:** Always start a NEW chat when testing. ChatGPT caches connector metadata.

### Enable Your Connector

1. Click **+** button
2. Select **More** → **Developer Mode**
3. **Enable** your Property Server connector

### Test Queries

Try these queries in order:

#### 1. Basic Query
```
Show me properties in DY4 under £100,000
```

**Expected behavior:**
- Tool `query_listings` is called
- Widget should render with property cards
- You should see images, prices, bedrooms
- Favorite buttons should work
- Sort dropdown should work

#### 2. Test Filters
```
Find 2-bedroom flats with parking in LE65
```

**Expected:**
- Filtered results
- Filter badges shown in widget

#### 3. Test State Persistence
```
(Favorite some properties, then ask:)
Show me more properties in the same area
```

**Expected:**
- Favorites persist across queries
- Widget state maintained

## Debugging

### If Widget Doesn't Render

#### Check 1: Tool is Called
In ChatGPT, you should see the tool being called. If not:
- Check connector is enabled
- Check server is running
- Check ngrok is active

#### Check 2: Server Logs
Look at your server terminal for:
```
INFO:     127.0.0.1:xxxxx - "POST /mcp/messages HTTP/1.1" 200 OK
```

#### Check 3: Widget URL
Test the widget URL directly in browser:
```
https://your-ngrok-url.ngrok-free.app/widget/property-list.html
```

Should show the widget (may show "Loading..." without data).

#### Check 4: Browser Console
In ChatGPT:
1. Open DevTools (F12)
2. Look for errors in Console
3. Check Network tab for failed requests

Common errors:
- `CORS error` → Check CORS headers
- `Failed to load resource` → Check widget URL
- `window.openai is undefined` → Widget not in iframe context

### If Tools Work But Widget Shows Text

This means:
- ✅ MCP connection works
- ✅ Tools are called
- ❌ Widget not rendering

**Possible causes:**
1. **ChatGPT doesn't support Apps SDK widgets in Chat Mode**
   - Solution: This is a ChatGPT limitation
   - Workaround: Accept text/JSON responses

2. **Widget URL not accessible**
   - Test: Open widget URL in browser
   - Fix: Check ngrok, check CORS

3. **MIME type not recognized**
   - Check: `Content-Type: text/html+skybridge`
   - Fix: Verify in curl response

4. **Annotation not working**
   - Check: `openai/outputTemplate` in tool definition
   - Try: Using full HTTP URL instead of `ui://` URI

## Advanced: Using Full HTTP URL

If `ui://widget/property-list.html` doesn't work, try using the full HTTP URL:

### Update server_apps_sdk.py

```python
# In list_tools(), change the annotation:
annotations={
    "readOnlyHint": True,
    "openai/outputTemplate": "https://your-ngrok-url.ngrok-free.app/widget/property-list.html",
    "openai/widgetAccessible": True,
}
```

This makes ChatGPT fetch the widget from HTTP instead of MCP Resources.

## Success Criteria

### ✅ Widget Renders Successfully

You should see:
- Property cards in a grid
- Property images
- Prices and details
- Favorite buttons (clickable)
- Sort dropdown (functional)
- Filter badges
- Responsive layout

### ✅ Interactivity Works

- Click favorite → heart fills in
- Change sort → properties reorder
- Favorites persist across queries

### ✅ State Management

- `window.openai.toolOutput` → Initial data
- `window.openai.widgetState` → Favorites/sort
- `window.openai.setWidgetState()` → Persists changes

## Troubleshooting Matrix

| Symptom | Cause | Solution |
|---------|-------|----------|
| Tool not called | Connector not enabled | Enable in chat |
| Tool called, no widget | Apps SDK not supported | Check ChatGPT docs |
| Widget shows "Loading..." | No data in toolOutput | Check tool response |
| CORS error | Wrong headers | Check server CORS config |
| Widget blank | JavaScript error | Check browser console |
| State not persisting | setWidgetState not called | Check hook implementation |

## Next Steps

### If Widget Works ✅

1. **Add more features:**
   - Property details modal
   - Map view
   - Comparison tool

2. **Improve UX:**
   - Loading states
   - Error handling
   - Empty states

3. **Deploy to production:**
   - Use permanent domain (not ngrok)
   - Add authentication
   - Monitor usage

### If Widget Doesn't Work ❌

1. **Verify ChatGPT Apps SDK support:**
   - Check OpenAI documentation
   - Look for official examples
   - Ask in OpenAI forums

2. **Try TypeScript SDK:**
   - Use official OpenAI examples
   - Rewrite server in TypeScript
   - Follow their exact patterns

3. **Accept text-only mode:**
   - Tools work perfectly
   - Users get all data
   - Just no custom UI

## Files Reference

- `server_apps_sdk.py` - Apps SDK server implementation
- `web/src/PropertyListWidget.tsx` - Main React component
- `web/src/hooks/useOpenAiGlobal.ts` - window.openai bridge
- `web/dist/component.js` - Built widget bundle (149KB)
- `tools.py` - Property query logic

## Documentation

- Apps SDK: https://developers.openai.com/apps-sdk/
- Custom UI: `docs/external/custom-ui.md`
- MCP Setup: `docs/external/mcpoai2.md`
- Component Design: `docs/external/plan-ui.md`

## Support

If you encounter issues:
1. Check server logs
2. Check browser console
3. Test widget URL directly
4. Verify ngrok is active
5. Try in NEW chat

Good luck! 🚀

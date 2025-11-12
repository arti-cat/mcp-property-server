# Property MCP Server - Apps SDK Edition

## What This Is

An **OpenAI Apps SDK** integration that displays property listings with a custom React widget in ChatGPT.

## Quick Start

```bash
# 1. Start server
./deploy_apps_sdk.sh

# 2. In another terminal, expose with ngrok
ngrok http 8000

# 3. Connect to ChatGPT
# Settings → Connectors → Create
# URL: https://your-ngrok-url.ngrok-free.app/mcp/

# 4. Test in NEW chat
# Enable connector and ask: "Show me properties in DY4 under £100,000"
```

## Architecture

### Components

1. **MCP Server** (`server_apps_sdk.py`)
   - Implements MCP protocol with SSE transport
   - 3 tools: `get_schema`, `query_listings`, `calculate_average_price`
   - Returns structured content for widget hydration

2. **Widget HTML Endpoint** (`/widget/property-list.html`)
   - Serves React widget bundle
   - CORS configured for ChatGPT
   - Apps SDK metadata in headers

3. **React Widget** (`web/src/`)
   - Uses `window.openai` API
   - Displays property cards
   - Favorites and sorting
   - State persistence

### Data Flow

```
User Query → ChatGPT → MCP Tool Call → Server Response → Widget Renders
                                            ↓
                                    structuredContent
                                            ↓
                                  window.openai.toolOutput
                                            ↓
                                    React Component
```

## Features

### Widget Features

- ✅ Property cards with images
- ✅ Favorite properties (persisted)
- ✅ Sort by price/bedrooms
- ✅ Filter badges
- ✅ Dark mode support
- ✅ Responsive layout

### MCP Tools

1. **query_listings** - Search and filter properties
   - Filters: postcode, price, bedrooms, garden, parking
   - Returns: Up to 5 properties with full details
   - Apps SDK: Links to widget via `openai/outputTemplate`

2. **get_schema** - Get data structure
   - Returns: Available fields and types

3. **calculate_average_price** - Price statistics
   - Filters: postcode, property type
   - Returns: Average price for matching properties

## Implementation Details

### Apps SDK Integration

**Tool Annotations:**
```python
annotations={
    "readOnlyHint": True,
    "openai/outputTemplate": "ui://widget/property-list.html",
    "openai/widgetAccessible": True,
    "openai/toolInvocation/invoking": "Searching properties...",
    "openai/toolInvocation/invoked": "Found properties"
}
```

**Tool Response Format:**
```python
{
    "content": [{"type": "text", "text": "Found 5 properties..."}],
    "structuredContent": {
        "properties": [...],
        "filters_applied": {...},
        "total_results": 5,
        "showing": 5
    },
    "_meta": {}
}
```

**Widget HTML:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="root"></div>
    <script type="module">{WIDGET_JS}</script>
</body>
</html>
```

### React Component

**Hooks:**
- `useOpenAiGlobal(key)` - Subscribe to window.openai values
- `useToolOutput()` - Read initial data
- `useWidgetState(default)` - Persist state across sessions
- `useTheme()` - Dark/light mode

**State Management:**
```typescript
const [widgetState, setWidgetState] = useWidgetState({
    favorites: [],
    hidden: [],
    sortBy: 'price_asc'
});

// Persists to ChatGPT automatically
setWidgetState(prev => ({
    ...prev,
    favorites: [...prev.favorites, propertyId]
}));
```

## Testing

### Local Testing

```bash
# Health check
curl http://localhost:8000/health

# Widget HTML
curl http://localhost:8000/widget/property-list.html

# CORS headers
curl -I http://localhost:8000/widget/property-list.html
```

### ChatGPT Testing

1. **Start NEW chat** (important!)
2. **Enable connector**
3. **Test queries:**
   - "Show me properties in DY4 under £100,000"
   - "Find 2-bedroom flats with parking"
   - "What's the average price in LE65?"

### Expected Behavior

**If widget renders ✅:**
- Property cards display
- Images load
- Favorites work
- Sort works
- State persists

**If widget doesn't render ❌:**
- Tool is called ✓
- Data is returned ✓
- But only text shows

This likely means ChatGPT's Apps SDK support is limited or the widget URL isn't being fetched.

## Troubleshooting

### Widget Not Rendering

**Check:**
1. Server running? `curl http://localhost:8000/health`
2. ngrok active? `curl http://localhost:4040/api/tunnels`
3. Widget URL accessible? Open in browser
4. CORS headers present? `curl -I ...`
5. Browser console errors? F12 in ChatGPT

**Common Issues:**
- **CORS error** → Check server CORS config
- **404 on widget** → Check endpoint path
- **Tool not called** → Enable connector in chat
- **Blank widget** → Check browser console

### Debugging Steps

1. **Verify server:**
   ```bash
   curl http://localhost:8000/health | python3 -m json.tool
   ```

2. **Test widget HTML:**
   ```bash
   curl http://localhost:8000/widget/property-list.html | head -20
   ```

3. **Check ngrok:**
   ```bash
   curl http://localhost:4040/api/tunnels | python3 -m json.tool
   ```

4. **Test in browser:**
   Open `https://your-ngrok-url.ngrok-free.app/widget/property-list.html`

## Files

### Server
- `server_apps_sdk.py` - Apps SDK server
- `tools.py` - Property query logic
- `data/listings.jsonl` - Property data (475 listings)

### Widget
- `web/src/PropertyListWidget.tsx` - Main component
- `web/src/PropertyCard.tsx` - Property card
- `web/src/hooks/` - React hooks
- `web/dist/component.js` - Built bundle (149KB)

### Documentation
- `APPS_SDK_DEPLOYMENT.md` - Deployment guide
- `docs/external/custom-ui.md` - Apps SDK UI docs
- `docs/external/mcpoai2.md` - MCP setup docs
- `docs/external/plan-ui.md` - Component design

## Development

### Rebuild Widget

```bash
cd web
npm run build
cd ..
```

### Update Server

Edit `server_apps_sdk.py` and restart.

### Test Changes

Always test in a **NEW chat** in ChatGPT to avoid cache issues.

## Production Deployment

### Requirements

1. **Permanent domain** (not ngrok)
2. **HTTPS** (required by ChatGPT)
3. **CORS** configured for `https://chatgpt.com`
4. **Monitoring** for uptime

### Deployment Options

- **Cloud Run** (Google Cloud)
- **Railway** (easy deployment)
- **Fly.io** (global edge)
- **AWS Lambda** (serverless)

### Environment Variables

```bash
export PORT=8000
export WIDGET_PATH=web/dist/component.js
export DATA_PATH=data/listings.jsonl
```

## Known Limitations

1. **ChatGPT Apps SDK support unclear**
   - Standard MCP doesn't include widgets
   - Apps SDK may be separate system
   - May only work with TypeScript SDK

2. **Widget rendering not guaranteed**
   - Depends on ChatGPT implementation
   - May show text instead of widget
   - Tools still work perfectly

3. **State scoped to widget instance**
   - Favorites don't transfer to new queries
   - Each tool call = new widget
   - Use `setWidgetState` to persist

## Next Steps

### If Widget Works ✅

1. Add more features (map view, details modal)
2. Improve UX (loading states, animations)
3. Deploy to production
4. Monitor usage

### If Widget Doesn't Work ❌

1. Verify ChatGPT Apps SDK support
2. Try TypeScript SDK
3. Accept text-only mode (tools still work!)
4. Wait for better Apps SDK documentation

## Support

- **OpenAI Apps SDK**: https://developers.openai.com/apps-sdk/
- **MCP Specification**: https://modelcontextprotocol.io/
- **Examples**: https://github.com/openai/openai-apps-sdk-examples

## License

MIT

---

**Built for OpenAI Apps SDK** | Property listings with custom React widgets

# Widget Deployment Guide

## Local Testing

### 1. Test the Widget Locally

```bash
cd web

# Open test.html in a browser
# On Linux:
xdg-open test.html

# Or use a local server:
python3 -m http.server 8080
# Then visit: http://localhost:8080/test.html
```

The test page includes:
- Mock `window.openai` API
- Sample property data
- Theme toggle (light/dark)
- Console logging for debugging

### 2. Verify Widget Features

- ✅ Properties display with images
- ✅ Price, bedrooms, postcode show correctly
- ✅ Garden/parking badges appear
- ✅ Favorite button works (check console)
- ✅ Sort dropdown changes order
- ✅ Dark mode toggle works
- ✅ Click property card opens detail URL

## ChatGPT Deployment

### Prerequisites

- ChatGPT Pro, Team, Enterprise, or Edu account
- Developer Mode enabled in ChatGPT settings
- MCP server running with HTTP transport
- ngrok or similar tunneling service

### Step 1: Build the Widget

```bash
cd web
npm run build
```

This creates `dist/component.js` (bundled React component).

### Step 2: Start the MCP Server

```bash
# From project root
python3 server.py --http
```

Server runs on `http://127.0.0.1:8000`

### Step 3: Expose with ngrok

```bash
ngrok http 8000
```

Note your public URL (e.g., `https://abc123.ngrok-free.dev`)

### Step 4: Configure ChatGPT Connector

1. Go to **ChatGPT Settings** → **Connectors**
2. Under **Advanced**, enable **Developer Mode**
3. Click **Create** to add a new connector:
   - **Name**: Property Server
   - **Server URL**: `https://your-ngrok-url.ngrok-free.dev/mcp/`
   - Check **I trust this provider**
   - Click **Create**

### Step 5: Test in ChatGPT

1. Start a new chat
2. Click **+** → **More** → **Developer Mode**
3. Enable your Property Server connector
4. Try queries like:
   - "Show me properties in DY4 under £100,000"
   - "Find 2-bedroom properties with parking"
   - "Properties in LE65 with gardens"

## Widget Response Format

The `query_listings` tool now returns:

```json
{
  "properties": [
    {
      "property_id": "32926983",
      "ld_name": "Potters Brook, Tipton",
      "ld_image": "https://...",
      "price_text": "£81,995",
      "price_amount": 81995,
      "bedrooms": 1,
      "bathrooms": 1,
      "property_type": "Apartment",
      "postcode": "DY4 7LG",
      "garden": true,
      "parking": false,
      "status": "Sold Subject to Contract",
      "detail_url": "https://..."
    }
  ],
  "filters_applied": {
    "postcode": "DY4",
    "max_price": 100000
  },
  "total_results": 47,
  "showing": 5
}
```

## Troubleshooting

### Widget Not Loading

1. Check browser console for errors
2. Verify `dist/component.js` exists and is recent
3. Check that server is returning widget metadata
4. Ensure ngrok URL is correct in ChatGPT connector

### Images Not Showing

- Images load lazily - scroll to trigger
- Fallback placeholder shows if image fails
- Check network tab for CORS issues

### Favorites Not Persisting

- Check console for `setWidgetState` calls
- Verify `window.openai.setWidgetState` is available
- Widget state is scoped to message instance

### Dark Mode Not Working

- Check that theme is being read from `window.openai.theme`
- Verify `data-theme` attribute on `<html>` element
- CSS variables should update automatically

## Development Workflow

### Making Changes

```bash
cd web

# Watch mode (auto-rebuild on changes)
npm run dev

# In another terminal, test locally
python3 -m http.server 8080
```

### Rebuild and Deploy

```bash
# 1. Make changes to React components
# 2. Rebuild
npm run build

# 3. Restart server (if needed)
# Server will automatically serve new bundle
```

### Testing Changes

1. **Local**: Open `test.html` in browser
2. **ChatGPT**: Refresh connector or start new chat

## Performance Tips

### Bundle Size

Current bundle: ~146KB (minified)

To reduce:
- Remove unused dependencies
- Lazy load heavy components
- Optimize images

### Widget State

Keep under 4k tokens:
- Only store property IDs in favorites
- Don't duplicate tool output
- Compress if needed

### Image Loading

- Use `loading="lazy"` (already implemented)
- Show placeholders while loading
- Handle errors gracefully

## Next Steps

### Planned Features

1. **Load More Button** - Fetch additional properties
2. **Filter Refinement** - Inline filter controls
3. **Property Comparison** - Side-by-side view
4. **Map View** - Geographic visualization (v2)

### Adding New Widgets

To add widgets for other tools:

1. Create new component in `web/src/`
2. Update tool response to include widget metadata
3. Build and test locally
4. Deploy to ChatGPT

See `docs/WIDGET_IMPLEMENTATION_PLAN.md` for details.

## Resources

- [ChatGPT Apps SDK Docs](https://platform.openai.com/docs/mcp)
- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Protocol](https://modelcontextprotocol.io)
- [React Documentation](https://react.dev)

## Support

For issues or questions:
1. Check browser console for errors
2. Review server logs
3. Test with `test.html` first
4. Verify ngrok tunnel is active

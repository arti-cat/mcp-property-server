# Property MCP Server

A FastMCP server for querying property listings with 475 properties.

**✨ Now with ChatGPT UI Widget!** Interactive property cards with favorites, sorting, and dark mode support.

**🎯 NEW: Lead Capture & CRM!** Capture leads, match clients to properties, schedule viewings, and manage your sales pipeline. See [LEAD_CAPTURE_FEATURE.md](LEAD_CAPTURE_FEATURE.md)

**🎨 Reusable Widget Templates!** Complete patterns and templates for building your own ChatGPT widgets. See [WIDGET_PATTERNS_SUMMARY.md](WIDGET_PATTERNS_SUMMARY.md)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with STDIO (for Claude Desktop)
python3 server.py

# Run with HTTP (for remote access)
python3 server.py --http
```

## Tools

### Property Search Tools

#### get_schema()
Returns the data schema for property listings.

#### query_listings(...)
Search and filter properties.

**Parameters:**
- `postcode` - Filter by postcode (e.g., "DY4 7LG")
- `property_type` - Filter by type (e.g., "Flat")
- `max_price` - Maximum price
- `min_bedrooms` - Minimum bedrooms
- `has_garden` - Must have garden
- `has_parking` - Must have parking
- `limit` - Max results (default: 5)

#### calculate_average_price(...)
Calculate average price for matching properties.

**Parameters:**
- `postcode` - Filter by postcode
- `property_type` - Filter by type

### Lead Capture & CRM Tools

#### capture_lead(...)
Capture new buyer or seller leads from conversations.

**Parameters:**
- `full_name`, `email`, `mobile`, `role` (required)
- `stage` - Lead stage (hot/warm/cold/instructed/completed)
- `budget_max`, `min_bedrooms` - For buyers
- `selling_property_id`, `asking_price` - For sellers

#### match_client(...)
Find properties matching a buyer's preferences.

**Parameters:**
- `client_id` (required) - Buyer's client ID
- `limit` - Max results (default: 10)

#### schedule_viewing(...)
Book property viewings with conflict detection.

**Parameters:**
- `property_id`, `buyer_client_id`, `datetime_iso` (required)
- `notes` - Optional viewing notes

#### view_leads(...)
View and filter client pipeline.

**Parameters:**
- `role` - Filter by buyer/seller
- `stage` - Filter by lead stage
- `limit` - Max results (default: 20)

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
python3 -m pytest test_server.py -v
```

## Transports

**STDIO (default)** - For Claude Desktop, Cursor
```bash
python3 server.py
```

**HTTP** - For remote access
```bash
python3 server.py --http
# Server at http://127.0.0.1:8000/mcp
```

## Project Structure

```
├── server.py           # Main FastMCP server
├── tools.py            # Tool implementations
├── data_loader.py      # Data loading
├── test_server.py      # Pytest tests
├── requirements.txt    # Dependencies
├── web/                # React UI widget (NEW!)
│   ├── src/            # React components
│   ├── dist/           # Built bundle
│   └── test.html       # Local testing
├── docs/               # Documentation
│   ├── WIDGET_IMPLEMENTATION_PLAN.md
│   ├── WIDGET_DEPLOYMENT.md
│   └── WIDGET_SUMMARY.md
└── data/
    └── listings.jsonl  # Property data (475 listings)
```

## Claude Desktop Setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "property-server": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

## ChatGPT Setup

### Requirements

- ChatGPT Pro, Team, Enterprise, or Edu account
- Developer Mode enabled in ChatGPT settings

### Setup Steps

1. **Start the server with HTTP transport:**

   ```bash
   python3 server.py --http
   ```

2. **Expose with ngrok:**

   ```bash
   ngrok http 8000
   ```

   Note your public URL (e.g., `https://abc123.ngrok-free.dev`)

3. **Enable Developer Mode in ChatGPT:**
   - Go to **Settings** → **Connectors**
   - Under **Advanced**, toggle **Developer Mode** to enabled

4. **Create Connector:**
   - In **Settings** → **Connectors**, click **Create**
   - **Name**: Property Server
   - **Server URL**: `https://your-ngrok-url.ngrok-free.dev/mcp/`
   - Check **I trust this provider**
   - Click **Create**

5. **Use in Chat:**
   - Start a new chat
   - Click **+** → **More** → **Developer Mode**
   - Enable your Property Server connector
   - Ask questions like:
     - "Show me properties in DY4 7LG under £100,000"
     - "Find flats with parking"
     - "What's the average price for 2-bedroom properties?"

### Features

- ✅ All 3 tools have `readOnlyHint` annotations (no confirmation prompts)
- ✅ Natural language queries
- ✅ 475 property listings
- ✅ Filter by postcode, type, price, bedrooms, garden, parking

## UI Widget

The server now includes an interactive React widget for ChatGPT:

**Features:**
- 🏠 Property cards with images
- ❤️ Favorite properties (persisted)
- 🔄 Sort by price or bedrooms
- 🌓 Dark mode support
- 📱 Responsive design

**Quick Start:**
```bash
# Build widget
cd web && npm install && npm run build

# Test locally
open test.html

# Deploy to ChatGPT
# See docs/WIDGET_DEPLOYMENT.md
```

**Documentation:**
- [Implementation Plan](docs/WIDGET_IMPLEMENTATION_PLAN.md)
- [Deployment Guide](docs/WIDGET_DEPLOYMENT.md)
- [Summary](docs/WIDGET_SUMMARY.md)

## Widget Templates

This project includes **complete reusable templates** for building ChatGPT Apps SDK widgets:

- **[WIDGET_PATTERNS_SUMMARY.md](WIDGET_PATTERNS_SUMMARY.md)** - Overview & quick start
- **[docs/WIDGET_TEMPLATE_GUIDE.md](docs/WIDGET_TEMPLATE_GUIDE.md)** - Complete implementation guide
- **[docs/REUSABLE_PATTERNS.md](docs/REUSABLE_PATTERNS.md)** - Quick reference
- **[docs/ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md)** - System architecture
- **[docs/create-widget-project.sh](docs/create-widget-project.sh)** - Project generator

**Create a new widget project:**
```bash
cd docs
./create-widget-project.sh my-widget-name
```

## Production Deployment

Deploy to persistent hosting with automatic HTTPS:

```bash
# Quick deploy to Fly.io
./deploy.sh

# Manual deployment
fly launch --no-deploy
fly deploy
```

**Supported Platforms:**
- ✅ Fly.io (recommended) - Free tier available
- ✅ Render - Auto-deploy from Git
- ✅ Railway - Simple pricing
- ✅ Google Cloud Run - Scale-to-zero

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.**

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [ChatGPT MCP Integration](https://gofastmcp.com/integrations/chatgpt.md)
- [ChatGPT Apps SDK](https://platform.openai.com/docs/mcp)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Deployment Guide](DEPLOYMENT.md)

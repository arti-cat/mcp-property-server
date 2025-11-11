# Property MCP Server

A FastMCP server for querying property listings with 475 properties.

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

### get_schema()
Returns the data schema for property listings.

### query_listings(...)
Search and filter properties.

**Parameters:**
- `postcode` - Filter by postcode (e.g., "DY4 7LG")
- `property_type` - Filter by type (e.g., "Flat")
- `max_price` - Maximum price
- `min_bedrooms` - Minimum bedrooms
- `has_garden` - Must have garden
- `has_parking` - Must have parking
- `limit` - Max results (default: 5)

### calculate_average_price(...)
Calculate average price for matching properties.

**Parameters:**
- `postcode` - Filter by postcode
- `property_type` - Filter by type

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

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [ChatGPT MCP Integration](https://gofastmcp.com/integrations/chatgpt.md)
- [MCP Protocol](https://modelcontextprotocol.io)

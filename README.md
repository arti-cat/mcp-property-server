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

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Protocol](https://modelcontextprotocol.io)

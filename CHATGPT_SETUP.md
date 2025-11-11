# ChatGPT Setup Guide

## Current Deployment

✅ **Server is running and ready to connect!**

- **Local Server**: `http://127.0.0.1:8000`
- **Public URL**: `https://unblemished-kaycee-downily.ngrok-free.dev`
- **MCP Endpoint**: `https://unblemished-kaycee-downily.ngrok-free.dev/mcp/`
- **Health Check**: `https://unblemished-kaycee-downily.ngrok-free.dev/health`

## Quick Setup (5 Steps)

### 1. Enable Developer Mode

1. Open ChatGPT
2. Go to **Settings** → **Connectors**
3. Under **Advanced**, toggle **Developer Mode** to **enabled**

### 2. Create Connector

1. In **Settings** → **Connectors**, click **Create**
2. Fill in:
   - **Name**: `Property Server`
   - **Server URL**: `https://unblemished-kaycee-downily.ngrok-free.dev/mcp/`
3. Check **I trust this provider**
4. Click **Create**

### 3. Start Using

1. Start a new chat
2. Click **+** button → **More** → **Developer Mode**
3. **Enable the Property Server connector** (must be done for each chat)
4. Start asking questions!

## Example Queries

Try these natural language questions:

- "Show me all properties in DY4 7LG"
- "Find flats under £100,000 with parking"
- "What's the average price for 2-bedroom properties?"
- "Show me properties with gardens in DY4 7LG"
- "Get the data schema for properties"

## Available Tools

All 3 tools have `readOnlyHint` annotations (no confirmation prompts):

1. **get_schema()** - Returns property data schema
2. **query_listings()** - Search and filter 475 properties
   - Filter by: postcode, type, price, bedrooms, garden, parking
3. **calculate_average_price()** - Calculate average prices

## Troubleshooting

### Server Not Responding

Check if server is running:

```bash
curl https://unblemished-kaycee-downily.ngrok-free.dev/health
```

Should return: `{"status":"healthy","service":"PropertyServer","version":"1.0.0"}`

### Restart Server

If needed:

```bash
# Terminal 1: Start server
python server.py --http

# Terminal 2: Start ngrok (if not running)
ngrok http 8000
```

### Connector Not Working

- Ensure Developer Mode is enabled in ChatGPT settings
- Verify the connector is enabled in the specific chat session
- Check the URL ends with `/mcp/` (not just `/mcp`)

## Requirements

- ChatGPT Pro, Team, Enterprise, or Edu account
- Developer Mode enabled (available in Connectors settings)

## Notes

- The connector must be explicitly enabled in each new chat session
- All tools are read-only and skip confirmation prompts
- Server has 475 property listings ready to query
- ngrok URL remains active as long as ngrok is running

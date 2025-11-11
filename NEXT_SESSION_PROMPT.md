# Next Session: Connect Property Server to ChatGPT

## Objective

Extend the Property MCP Server to work with ChatGPT in both Chat Mode and Deep Research Mode using HTTP transport.

## Current State

We have a working FastMCP server with:
- ✅ 3 tools: `get_schema`, `query_listings`, `calculate_average_price`
- ✅ HTTP transport working (`python3 server.py --http`)
- ✅ 475 property listings in JSONL format
- ✅ Comprehensive tests and documentation

## What We Need to Add

### For ChatGPT Chat Mode
Our existing tools should work, but we need to:
1. Deploy server with public URL (using ngrok)
2. Add `readOnlyHint` annotations to read-only tools
3. Test connection with ChatGPT Developer Mode

### For ChatGPT Deep Research Mode
We MUST implement these two specific tools:

```python
@mcp.tool()
def search(query: str) -> dict:
    """
    Search for properties matching the query.
    Must return {"ids": [list of string IDs]}
    """
    # Search through 475 properties
    # Return matching property_ids
    return {"ids": ["prop1", "prop2", "prop3"]}

@mcp.tool()
def fetch(id: str) -> dict:
    """
    Fetch a complete property record by ID.
    Return the full property data for ChatGPT to analyze.
    """
    # Fetch property by property_id
    return {
        "id": id,
        "title": "Property Title",
        "content": "Full property details...",
        "metadata": {...}
    }
```

## Requirements from ChatGPT Documentation

**Chat Mode:**
- ✅ HTTP transport on public URL
- ✅ MCP endpoint at `/mcp/`
- ⚠️ Need Developer Mode enabled in ChatGPT
- ⚠️ Need to add `readOnlyHint` annotations

**Deep Research Mode:**
- ❌ MUST have `search` tool returning `{"ids": [...]}`
- ❌ MUST have `fetch` tool returning full record
- ⚠️ Without these, ChatGPT will reject the server

## Tasks for Next Session

### 1. Add ChatGPT-Compatible Tools

```python
# In server.py, add these tools:

@mcp.tool()
def search(query: str) -> dict:
    """Search for properties matching the query."""
    # Use existing query_listings logic
    # Extract property_ids from results
    # Return {"ids": [list of ids]}
    pass

@mcp.tool()
def fetch(id: str) -> dict:
    """Fetch complete property record by ID."""
    # Find property by property_id
    # Return full property data with metadata
    pass
```

### 2. Add Read-Only Annotations

```python
@mcp.tool(annotations={"readOnlyHint": True})
def get_schema() -> dict:
    """Returns the data schema for property listings."""
    return tools.get_schema()

@mcp.tool(annotations={"readOnlyHint": True})
def query_listings(...) -> list:
    """Searches and filters property listings."""
    return tools.query_listings(...)

@mcp.tool(annotations={"readOnlyHint": True})
def calculate_average_price(...) -> dict:
    """Calculates average price."""
    return tools.calculate_average_price(...)
```

### 3. Deploy with ngrok

```bash
# Terminal 1
python3 server.py --http

# Terminal 2
ngrok http 8000

# Note the public URL: https://abc123.ngrok.io
```

### 4. Connect to ChatGPT

**For Chat Mode:**
1. Enable Developer Mode in ChatGPT Settings → Connectors → Advanced
2. Create connector with URL: `https://abc123.ngrok.io/mcp/`
3. Start new chat → + → More → Developer Mode
4. Enable the connector
5. Test: "Show me properties in DY4 7LG"

**For Deep Research:**
1. Same connector setup
2. Start new chat → + → Deep Research
3. Select Property Server as source
4. Test: "Research property prices in DY4 7LG area"

### 5. Test and Verify

- [ ] Chat Mode works with existing tools
- [ ] Deep Research finds properties via `search`
- [ ] Deep Research retrieves details via `fetch`
- [ ] Citations work properly
- [ ] Read-only tools skip confirmations

## Implementation Notes

### Search Tool Design

The `search` tool should:
- Parse natural language query
- Search across: postcode, property_type, price range, bedrooms
- Return list of matching `property_id` values
- Format: `{"ids": ["id1", "id2", ...]}`

### Fetch Tool Design

The `fetch` tool should:
- Look up property by `property_id`
- Return complete property data
- Include metadata (price, bedrooms, postcode, etc.)
- Format for ChatGPT citation

### Data Structure

Our properties have:
```python
{
    "property_id": "string",
    "price_amount": number,
    "bedrooms": number,
    "bathrooms": number,
    "property_type": "string",
    "postcode": "string",
    "garden": boolean,
    "parking": boolean,
    "status": "string",
    "overview": ["list"],
    "description": "string"
}
```

## Reference Documentation

**IMPORTANT: Always verify against official docs!**

- ChatGPT MCP Guide: https://platform.openai.com/docs/mcp
- Developer Mode Guide: https://platform.openai.com/docs/guides/developer-mode
- FastMCP Docs: https://gofastmcp.com
- FastMCP LLMs: https://gofastmcp.com/llms.txt
- MCP Protocol: https://modelcontextprotocol.io
- MCP Protocol LLMs: https://modelcontextprotocol.io/llms-full.txt

## Success Criteria

✅ Server accessible via ngrok public URL
✅ ChatGPT Chat Mode can use all 5 tools (3 existing + search + fetch)
✅ ChatGPT Deep Research can search and fetch properties
✅ Read-only tools skip confirmation prompts
✅ Citations work properly in Deep Research
✅ Tests updated for new tools
✅ Documentation updated

## Files to Modify

- `server.py` - Add search/fetch tools, add annotations
- `tools.py` - Implement search/fetch logic
- `test_server.py` - Add tests for new tools
- `README.md` - Add ChatGPT setup instructions
- `NOTES.md` - Document ChatGPT integration learnings

## Key Reminder

**Check the official ChatGPT MCP documentation first!** Requirements may have changed since this prompt was written. The official docs are the source of truth.

## Questions to Answer

1. How should we parse natural language queries in `search`?
2. What format works best for `fetch` results?
3. Should we keep the existing tools or only use search/fetch?
4. How to handle authentication if needed?
5. What's the best way to structure property data for citations?

## Start the Session With

"I want to extend the Property MCP Server to work with ChatGPT. I have NEXT_SESSION_PROMPT.md with the plan. Let's start by checking the official ChatGPT MCP documentation to verify requirements, then implement the search and fetch tools for Deep Research mode."

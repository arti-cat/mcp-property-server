# Next Session: Connect Property Server to ChatGPT Chat Mode

## Objective

Connect the Property MCP Server to ChatGPT Chat Mode using HTTP transport and ngrok.

## Current State

We have a working FastMCP server with:
- ✅ 3 tools: `get_schema`, `query_listings`, `calculate_average_price`
- ✅ HTTP transport working (`python3 server.py --http`)
- ✅ 475 property listings in JSONL format
- ✅ Comprehensive tests and documentation

## What We Need to Do

Our existing 3 tools will work perfectly in Chat Mode! We just need to:

1. ✅ Add `readOnlyHint` annotations (skip confirmation prompts)
2. ✅ Deploy server with ngrok (public URL)
3. ✅ Enable Developer Mode in ChatGPT
4. ✅ Create connector and test

**No new tools required!** Chat Mode works with any tools you define.

## Requirements from ChatGPT Documentation

**Chat Mode Requirements:**
- ✅ HTTP transport on public URL (we have this)
- ✅ MCP endpoint at `/mcp/` (we have this)
- ⚠️ Developer Mode must be enabled in ChatGPT Settings
- ⚠️ Add `readOnlyHint` annotations to skip confirmations

**Note:** Deep Research Mode requires `search` and `fetch` tools, but we're focusing on Chat Mode first. We can add Deep Research later if needed.

## Tasks for Next Session

### 1. Add Read-Only Annotations

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

### 2. Deploy with ngrok

```bash
# Terminal 1
python3 server.py --http

# Terminal 2
ngrok http 8000

# Note the public URL: https://abc123.ngrok.io
```

### 3. Connect to ChatGPT

1. Enable Developer Mode in ChatGPT Settings → Connectors → Advanced
2. Create connector with URL: `https://abc123.ngrok.io/mcp/`
3. Start new chat → + → More → Developer Mode
4. Enable the connector
5. Test: "Show me properties in DY4 7LG under £100,000"

### 4. Test and Verify

- [ ] Server accessible via ngrok URL
- [ ] Connector created in ChatGPT
- [ ] Developer Mode enabled in chat
- [ ] All 3 tools work in conversation
- [ ] Read-only tools skip confirmation prompts
- [ ] Can query properties naturally

## Implementation Notes

### Read-Only Hint Annotation

The `readOnlyHint` annotation tells ChatGPT that a tool is safe and doesn't modify data:
- Skips confirmation prompts
- Makes conversations smoother
- Use for: queries, calculations, read operations
- Don't use for: writes, deletes, modifications

### Example Queries to Test

Once connected, try these in ChatGPT:
- "Show me all properties in DY4 7LG"
- "Find flats under £100,000 with parking"
- "What's the average price for 2-bedroom properties?"
- "Show me properties with gardens in DY4 7LG"
- "Get the data schema for properties"

## Reference Documentation

**IMPORTANT: Always verify against official docs!**

- FastMCP Docs: https://gofastmcp.com
- FastMCP LLMs: https://gofastmcp.com/llms.txt
- FastMCP Testing: https://gofastmcp.com/patterns/testing
- FastMCP Transports: https://gofastmcp.com/deployment/running-server
- MCP Protocol: https://modelcontextprotocol.io
- MCP Protocol LLMs: https://modelcontextprotocol.io/llms-full.txt
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- ChatGPT MCP Guide: https://platform.openai.com/docs/mcp
- Developer Mode Guide: https://platform.openai.com/docs/guides/developer-mode

## Success Criteria

✅ Server accessible via ngrok public URL
✅ ChatGPT Chat Mode can use all 3 tools
✅ Read-only tools skip confirmation prompts
✅ Can query properties naturally in conversation
✅ Documentation updated with ChatGPT setup

## Files to Modify

- `server.py` - Add `readOnlyHint` annotations to existing tools
- `README.md` - Add ChatGPT Chat Mode setup instructions
- `NOTES.md` - Document ChatGPT integration learnings

## Optional: Add Deep Research Later

If you want Deep Research mode later, you'll need to add:
- `search(query: str) -> dict` - Returns `{"ids": [...]}`
- `fetch(id: str) -> dict` - Returns full property record

But for Chat Mode, our existing tools are perfect!

## Key Reminder

**Check the official ChatGPT MCP documentation first!** Requirements may have changed since this prompt was written. The official docs are the source of truth.

## Questions to Consider

1. Should we add authentication for the public ngrok URL?
2. Do we want to add rate limiting?
3. Should we log tool usage for analytics?
4. Any other tools we want to add for ChatGPT?

## Start the Session With

"I want to connect the Property MCP Server to ChatGPT Chat Mode. I have NEXT_SESSION_PROMPT.md with the plan. Let's start by checking the official ChatGPT MCP documentation to verify requirements, then add readOnlyHint annotations to our existing tools and deploy with ngrok."

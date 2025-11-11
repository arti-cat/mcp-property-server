# Project Notes

## What This Is

A FastMCP server that provides 3 tools for querying 475 property listings:
- `get_schema()` - Returns the data schema
- `query_listings()` - Search/filter properties by postcode, price, bedrooms, etc.
- `calculate_average_price()` - Calculate average prices for filtered properties

## Key Learning: Always Check Official Docs

### The Documentation Verification Process

When building with FastMCP (or any framework), **always verify against official documentation**:

1. **Official FastMCP Docs**: https://gofastmcp.com
2. **MCP Protocol Spec**: https://modelcontextprotocol.io

### What We Learned By Checking Docs

#### ❌ Initial Approach (Wrong)
- Used curl/bash scripts for testing
- Thought "Missing session ID" was a bug
- Confused SSE transport with HTTP transport

#### ✅ After Checking Official Docs (Correct)

**Testing:**
- Official recommendation: Use FastMCP Client with pytest
- See: https://gofastmcp.com/patterns/testing.md
- Our implementation: `test_server.py` with 13 tests

**Transports:**
- `transport="http"` = Streamable HTTP (modern, recommended)
- `transport="sse"` = Legacy (backward compatibility only)
- Both use SSE internally, but HTTP is the full-featured version
- See: https://gofastmcp.com/deployment/running-server

**Session Management:**
- "Missing session ID" is NOT a bug - it's the MCP protocol requirement
- HTTP transport requires session initialization (security feature)
- See: https://spec.modelcontextprotocol.io/specification/2025-06-18/basic/transports/#streamable-http

## Quick Reference

### Run the Server
```bash
# For Claude Desktop (STDIO)
python3 server.py

# For remote access (HTTP)
python3 server.py --http
```

### Test the Server
```bash
# Official approach (recommended)
python3 -m pytest test_server.py -v

# HTTP transport testing (educational)
./test_endpoints.sh
```

### Add to Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
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

## Documentation Checklist for Future Work

When adding features or debugging:

- [ ] Check official FastMCP docs first
- [ ] Verify against MCP protocol spec if needed
- [ ] Look for official examples in FastMCP repo
- [ ] Don't assume - confirm with documentation
- [ ] If something seems wrong, it might be correct protocol behavior

## Important Files

- `server.py` - Main server with transport selection
- `tools.py` - Tool implementations
- `test_server.py` - Official testing approach (FastMCP Client)
- `test_endpoints.sh` - HTTP transport verification
- `data/listings.jsonl` - 475 property records

## Common Mistakes to Avoid

1. **Don't use curl for primary testing** - Use FastMCP Client
2. **Don't think session management is a bug** - It's required by MCP protocol
3. **Don't confuse `transport="sse"` with modern HTTP** - Use `transport="http"`
4. **Don't skip the official docs** - They have the answers

## Resources

- FastMCP Docs: https://gofastmcp.com
- FastMCP LLMs: https://gofastmcp.com/llms.txt
- FastMCP Testing: https://gofastmcp.com/patterns/testing
- FastMCP Transports: https://gofastmcp.com/deployment/running-server
- MCP Protocol: https://modelcontextprotocol.io
- MCP Protocol LLMs: https://modelcontextprotocol.io/llms-full.txt
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- ChatGPT MCP Guide: https://platform.openai.com/docs/mcp
- Developer Mode Guide: https://platform.openai.com/docs/guides/developer-mode

## Future Me / Future AI

If you're debugging or adding features:

1. **Read the official docs first** - Don't guess
2. **Check the FastMCP repo** for examples
3. **Verify protocol compliance** if working with transports
4. **Use FastMCP Client for testing** - Not curl
5. **Session management is normal** - Not a bug

The time spent reading documentation upfront saves hours of debugging later.

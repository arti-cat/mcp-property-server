# MCP & FastMCP Learnings - High-Level Overview

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that connects AI assistants to external data sources and tools. Think of it as a universal adapter that lets ChatGPT, Claude, and other AI models access your applications, databases, and services.

### Key Concepts

- **Protocol**: Standardized way for AI models to discover and use tools
- **Transport**: How the AI communicates with your server (STDIO, HTTP, SSE)
- **Tools**: Functions the AI can call (like API endpoints)
- **Resources**: Static or dynamic data the AI can read
- **Prompts**: Reusable prompt templates

## What is FastMCP?

**FastMCP** is a Python framework that makes building MCP servers incredibly simple. It's like FastAPI but for MCP servers.

### Why FastMCP?

- **Simple**: Decorator-based API (`@mcp.tool`)
- **Fast**: Built on modern async Python
- **Flexible**: Supports multiple transports (STDIO, HTTP, SSE)
- **Well-documented**: Excellent docs at https://gofastmcp.com
- **OpenAI-endorsed**: Used in OpenAI's official MCP examples

### Basic Structure

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def my_function(arg: str) -> dict:
    """Tool description here"""
    return {"result": "data"}

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
```

## MCP Transports

### STDIO (Standard Input/Output)
- **Use for**: Claude Desktop, Cursor, local IDE integrations
- **How it works**: Process-to-process communication
- **Pros**: Simple, secure, no network needed
- **Cons**: Can't access remotely

### HTTP (Streamable HTTP)
- **Use for**: ChatGPT, remote access, web integrations
- **How it works**: HTTP with Server-Sent Events (SSE)
- **Pros**: Remote access, works through ngrok, modern standard
- **Cons**: Requires public URL for ChatGPT

### SSE (Legacy)
- **Use for**: Backward compatibility only
- **Note**: HTTP transport is the modern replacement

## Tools: The Core of MCP

### What is a Tool?

A tool is a function that the AI can call. It's like an API endpoint but designed for AI consumption.

### Tool Anatomy

```python
@mcp.tool(annotations={"readOnlyHint": True})
def query_data(
    filter: str | None = None,
    limit: int = 5
) -> list:
    """
    Use this when the user wants to search data.
    
    Args:
        filter: What to search for
        limit: Max results (default: 5)
    """
    return results
```

### Critical Tool Design Principles

1. **Action-Oriented Descriptions**
   - ❌ Bad: "Returns property data"
   - ✅ Good: "Use this when the user wants to find properties for sale"

2. **"Use this when..." Format**
   - Tells the AI exactly when to invoke the tool
   - Improves discovery and reduces false positives

3. **Explicit Parameter Documentation**
   - Explain formats, ranges, examples
   - Clarify optional vs required
   - Show what partial matches work

4. **Include Example Queries**
   - "Perfect for queries like 'find properties in London'"
   - Helps AI understand natural language mapping

5. **One Job Per Tool**
   - Don't create kitchen-sink tools
   - Separate read and write operations
   - Makes confirmation flows cleaner

## Discovery: How AI Finds Your Tools

### What Influences Discovery?

1. **Server Instructions** - High-level description of what your server does
2. **Tool Names** - Action-oriented, unique names
3. **Tool Descriptions** - "Use this when..." format
4. **Parameter Docs** - Clear argument descriptions
5. **Conversation Context** - Chat history and previous results
6. **Brand Mentions** - User explicitly naming your app

### Discovery Best Practices

```python
# ❌ Generic - AI won't know when to use this
mcp = FastMCP(
    name="DataServer",
    instructions="A server for data."
)

# ✅ Action-oriented - AI knows exactly when to use this
mcp = FastMCP(
    name="PropertyServer",
    instructions="Use this server when the user wants to search for properties for sale, find homes in specific areas, or check property prices. Has 475 UK property listings."
)
```

### Named Mention
- User says your app name → Your app surfaces automatically
- Must be at beginning of prompt

### In-Conversation Discovery
- AI evaluates: context, metadata, user linking state
- Your tool descriptions are critical here

## OpenAI MCP Integration (ChatGPT)

### Two Modes

#### Chat Mode
- **Use for**: Interactive conversations with tools
- **Requirements**: 
  - Developer Mode enabled (Pro/Team/Enterprise/Edu)
  - HTTP transport with public URL
  - Connector created in Settings
- **Tools**: Any tools you define work
- **Confirmation**: Use `readOnlyHint` to skip prompts

#### Deep Research Mode
- **Use for**: Systematic information retrieval
- **Requirements**:
  - Must have `search()` and `fetch()` tools
  - Specific return format: `{"ids": [...]}`
- **Note**: Only uses search/fetch, ignores other tools

### ChatGPT Setup Flow

1. Deploy server with HTTP transport
2. Expose via ngrok (or public URL)
3. Enable Developer Mode in ChatGPT Settings
4. Create connector with URL: `https://your-url/mcp/`
5. In chat: + → More → Developer Mode → Enable connector
6. Connector must be enabled per chat session

### readOnlyHint Annotation

```python
@mcp.tool(annotations={"readOnlyHint": True})
def get_data() -> dict:
    """Read-only tool - skips confirmation"""
    return data

@mcp.tool()  # No annotation
def delete_data(id: str) -> str:
    """Write tool - may ask for confirmation"""
    return f"Deleted {id}"
```

## Common Patterns

### Fat Server Pattern
- Load all data once at startup
- Filter in Python (not database queries)
- Fast, simple, works for small-medium datasets
- Used in our property server (475 listings)

### Partial Matching
```python
# Allow flexible searches
if postcode and not listing['postcode'].upper().startswith(postcode.upper()):
    continue  # "LE65" matches "LE65 1DA", "LE65 2AY", etc.
```

### Limit Results
```python
# Always limit to save tokens
return filtered_results[:limit]  # Default: 5
```

### Health Check Endpoint
```python
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy"})
```

## Testing Strategies

### Local Testing
```python
# Use FastMCP Client with pytest
from fastmcp.client import FastMCPClient

async with FastMCPClient(server) as client:
    result = await client.call_tool("query_listings", {"postcode": "LE65"})
    assert len(result) > 0
```

### HTTP Testing
```bash
# Health check
curl https://your-url/health

# Don't use curl for MCP endpoints - use FastMCP Client
# MCP protocol requires session management
```

### Golden Prompt Testing
- Create list of expected user queries
- Test each in ChatGPT Developer Mode
- Verify correct tool selection
- Iterate on descriptions based on results

## Key Mistakes to Avoid

### 1. Generic Tool Descriptions
❌ "Returns data"
✅ "Use this when the user wants to search for properties"

### 2. Exact String Matching
❌ `if postcode == "LE65"`
✅ `if postcode.startswith("LE65")`

### 3. Missing Parameter Context
❌ `postcode: str` (no explanation)
✅ `postcode: Partial UK postcode (e.g., "LE65" matches "LE65 1DA")`

### 4. Kitchen-Sink Tools
❌ One tool that does everything
✅ Separate tools for read/write, different operations

### 5. Skipping Documentation
❌ Assuming the AI will figure it out
✅ Read official docs first, they have the answers

### 6. Testing with curl
❌ Using curl for MCP endpoints
✅ Use FastMCP Client or ChatGPT

### 7. Forgetting Session Management
❌ Thinking "Missing session ID" is a bug
✅ It's required by MCP protocol for HTTP transport

## Project Structure Best Practices

```
mcp-server/
├── server.py           # FastMCP server with tool decorators
├── tools.py            # Tool implementation logic
├── data_loader.py      # Data loading (fat server pattern)
├── test_server.py      # Pytest tests with FastMCP Client
├── requirements.txt    # Dependencies
├── README.md           # Setup instructions
└── data/
    └── data.jsonl      # Your data
```

## Resources & Documentation

### Official Documentation
- **FastMCP**: https://gofastmcp.com
- **FastMCP LLMs.txt**: https://gofastmcp.com/llms.txt
- **MCP Protocol**: https://modelcontextprotocol.io
- **ChatGPT MCP**: https://gofastmcp.com/integrations/chatgpt.md
- **FastMCP GitHub**: https://github.com/jlowin/fastmcp

### Key Pages
- **Testing**: https://gofastmcp.com/patterns/testing
- **Transports**: https://gofastmcp.com/deployment/running-server
- **Tool Design**: Focus on discovery and metadata

## Quick Reference

### Start Server
```bash
# STDIO (Claude Desktop)
python3 server.py

# HTTP (ChatGPT)
python3 server.py --http
```

### Deploy with ngrok
```bash
# Terminal 1
python3 server.py --http

# Terminal 2
ngrok http 8000
```

### Test with pytest
```bash
python3 -m pytest test_server.py -v
```

### Check Health
```bash
curl https://your-url/health
```

## Success Criteria

### Good Tool Design
- ✅ Action-oriented descriptions
- ✅ "Use this when..." format
- ✅ Clear parameter documentation
- ✅ Example queries included
- ✅ One focused job per tool

### Good Discovery
- ✅ Server instructions explain when to use
- ✅ Tool names are action-oriented
- ✅ Metadata helps AI disambiguate
- ✅ Golden prompts tested and working

### Good Implementation
- ✅ Tests pass with FastMCP Client
- ✅ Health endpoint responds
- ✅ Logs show tool invocations
- ✅ Results returned in expected format
- ✅ Documentation up to date

## The Golden Rule

**Always check official documentation first.** The time spent reading docs upfront saves hours of debugging later. FastMCP and MCP docs are comprehensive and accurate - use them.

## What We Built

A property search MCP server with:
- 475 UK property listings
- 3 tools: `get_schema`, `query_listings`, `calculate_average_price`
- HTTP transport for ChatGPT integration
- Action-oriented descriptions for better discovery
- Partial postcode matching for flexible searches
- `readOnlyHint` annotations for smooth UX

**Result**: ChatGPT can now search properties, filter by location/price/features, and calculate averages through natural language queries.

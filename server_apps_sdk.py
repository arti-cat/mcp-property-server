"""Property MCP Server - OpenAI Apps SDK Implementation

Based on the official OpenAI Apps SDK Python example (pizzaz_server_python).
This server uses FastMCP with custom request handlers to properly support Apps SDK widgets.

Key Apps SDK features:
1. Resources with _meta fields for widget configuration
2. Tool responses with {content, structuredContent, _meta}
3. MIME type: text/html+skybridge
4. Streamable HTTP transport for ChatGPT

Run with: python3 server_apps_sdk.py
"""
from pathlib import Path
from typing import Any, Dict, List
import mcp.types as types
from mcp.server.fastmcp import FastMCP
import tools
import json

# --- Constants ---
MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/property-list.html"

# --- Load UI bundle ---
WIDGET_HTML = ""
widget_path = Path("web/dist/component.js")
if widget_path.exists():
    widget_js = widget_path.read_text(encoding="utf-8")
    WIDGET_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div id="root"></div>
    <script type="module">{widget_js}</script>
</body>
</html>"""
    print(f"✅ Widget bundle loaded: {len(widget_js):,} bytes")
else:
    print("❌ Widget bundle not found at web/dist/component.js")
    print("   Run: cd web && npm run build")

# --- Create FastMCP Server ---
mcp = FastMCP(
    name="PropertyServer",
    stateless_http=True,  # Required for ChatGPT
)

# --- Helper functions for Apps SDK metadata ---
def _tool_meta() -> Dict[str, Any]:
    """Apps SDK metadata for tools."""
    return {
        "openai/outputTemplate": WIDGET_URI,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai/toolInvocation/invoking": "Searching properties...",
        "openai/toolInvocation/invoked": "Found properties",
    }

# --- Register Tools with Apps SDK metadata ---
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List available tools with Apps SDK annotations."""
    return [
        types.Tool(
            name="query_listings",
            title="Search Property Listings",
            description="Search and filter 475 property listings by location, price, bedrooms, garden, and parking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {"type": "string", "description": "Partial or full UK postcode (e.g., 'DY4' or 'LE65')"},
                    "property_type": {"type": "string", "description": "Type of property (e.g., 'Flat', 'House')"},
                    "max_price": {"type": "integer", "description": "Maximum price in GBP"},
                    "min_bedrooms": {"type": "integer", "description": "Minimum number of bedrooms"},
                    "has_garden": {"type": "boolean", "description": "Must have garden"},
                    "has_parking": {"type": "boolean", "description": "Must have parking"},
                    "limit": {"type": "integer", "description": "Max results (default: 5)", "default": 5}
                }
            },
            _meta=_tool_meta(),
            annotations={
                "readOnlyHint": True,
                "destructiveHint": False,
                "openWorldHint": False,
            },
        ),
        types.Tool(
            name="get_schema",
            title="Get Property Schema",
            description="Returns the data schema for property listings showing all searchable fields.",
            inputSchema={
                "type": "object",
                "properties": {}
            },
            annotations={
                "readOnlyHint": True,
            },
        ),
        types.Tool(
            name="calculate_average_price",
            title="Calculate Average Price",
            description="Calculate average price for properties matching the given postcode or property type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {"type": "string", "description": "Partial or full UK postcode"},
                    "property_type": {"type": "string", "description": "Type of property"}
                }
            },
            annotations={
                "readOnlyHint": True,
            },
        ),
    ]

# --- Register Resources with Apps SDK metadata ---
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List available resources with Apps SDK metadata."""
    return [
        types.Resource(
            name="Property List Widget",
            title="Property List Widget",
            uri=WIDGET_URI,
            description="Interactive property listing widget with favorites, sorting, and filters",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(),
        )
    ]

# --- Custom Resource Handler ---
async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests with Apps SDK format."""
    if str(req.params.uri) != WIDGET_URI:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )
    
    contents = [
        types.TextResourceContents(
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
            text=WIDGET_HTML,
            _meta=_tool_meta(),
        )
    ]
    
    return types.ServerResult(types.ReadResourceResult(contents=contents))

# --- Custom Tool Handler ---
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool calls with Apps SDK format."""
    tool_name = req.params.name
    arguments = req.params.arguments or {}
    
    if tool_name == "get_schema":
        result = tools.get_schema()
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ],
            )
        )
    
    elif tool_name == "query_listings":
        result = tools.query_listings(
            postcode=arguments.get("postcode"),
            property_type=arguments.get("property_type"),
            max_price=arguments.get("max_price"),
            min_bedrooms=arguments.get("min_bedrooms"),
            has_garden=arguments.get("has_garden"),
            has_parking=arguments.get("has_parking"),
            limit=arguments.get("limit", 5)
        )
        
        # Apps SDK format: content + structuredContent + _meta
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Found {result['total_results']} properties matching your criteria.",
                    )
                ],
                structuredContent=result.get("structuredContent", result),
                _meta={
                    "openai/toolInvocation/invoked": "Found properties",
                },
            )
        )
    
    elif tool_name == "calculate_average_price":
        result = tools.calculate_average_price(
            postcode=arguments.get("postcode"),
            property_type=arguments.get("property_type")
        )
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ],
            )
        )
    
    # Unknown tool
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Unknown tool: {tool_name}",
                )
            ],
            isError=True,
        )
    )

# --- Register Custom Handlers ---
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

# --- Create Streamable HTTP App ---
app = mcp.streamable_http_app()

# --- Add CORS for ChatGPT ---
try:
    from starlette.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to https://chatgpt.com
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception as e:
    print(f"Warning: Could not add CORS middleware: {e}")

# --- Main ---
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("Property MCP Server - OpenAI Apps SDK")
    print("=" * 70)
    print(f"Mode: Apps SDK with Custom Widgets")
    print(f"Port: 8000")
    print(f"Transport: Streamable HTTP (ChatGPT compatible)")
    print()
    print("Endpoints:")
    print(f"  MCP: http://0.0.0.0:8000/mcp/")
    print()
    print("Widget Status:")
    if WIDGET_HTML:
        print(f"  ✅ Loaded")
    else:
        print(f"  ❌ Not loaded - run: cd web && npm run build")
    print()
    print("Next Steps:")
    print("  1. Expose with ngrok: ngrok http 8000")
    print("  2. In ChatGPT, create connector with: https://your-url.ngrok.io/mcp/")
    print("  3. Test with: 'Show me properties in DY4 under £100,000'")
    print("=" * 70)
    
    uvicorn.run("server_apps_sdk:app", host="0.0.0.0", port=8000)

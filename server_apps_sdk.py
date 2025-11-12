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
css_path = Path("web/src/styles/index.css")

if widget_path.exists():
    widget_js = widget_path.read_text(encoding="utf-8")
    
    # Load CSS if available
    widget_css = ""
    if css_path.exists():
        widget_css = css_path.read_text(encoding="utf-8")
        print(f"✅ Widget CSS loaded: {len(widget_css):,} bytes")
    
    WIDGET_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{widget_css}</style>
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
            description="Use this when the user wants to find, search, browse, or view properties for sale in the UK. Searches 475 property listings with filters for location (postcode like 'DY4' or 'LE65'), price range, number of bedrooms, garden availability, parking availability, and property type. Perfect for queries like 'find properties in Ashby', 'show me 2-bed houses under £200k', 'properties with gardens in DY4', or 'flats with parking'. Do not use for property valuations, mortgage calculations, or rental properties.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {
                        "type": "string", 
                        "description": "Partial or full UK postcode to filter by location. Examples: 'DY4', 'LE65', 'DY4 7LG'. Leave empty to search all locations."
                    },
                    "property_type": {
                        "type": "string", 
                        "description": "Type of property to filter by. Examples: 'Flat', 'House', 'Bungalow', 'Detached', 'Semi-Detached', 'Terraced'. Leave empty for all types."
                    },
                    "max_price": {
                        "type": "integer", 
                        "description": "Maximum price in GBP (British Pounds). Example: 200000 for properties under £200,000. Leave empty for no maximum."
                    },
                    "min_bedrooms": {
                        "type": "integer", 
                        "description": "Minimum number of bedrooms required. Examples: 2 for 2+ bedrooms, 3 for 3+ bedrooms. Leave empty for any number."
                    },
                    "has_garden": {
                        "type": "boolean", 
                        "description": "Set to true to only show properties with a garden. Leave empty or false for all properties."
                    },
                    "has_parking": {
                        "type": "boolean", 
                        "description": "Set to true to only show properties with parking. Leave empty or false for all properties."
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return. Default is 5. Use higher values (10-20) for broader searches.",
                        "default": 5
                    }
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
            title="Get Property Data Schema",
            description="Use this when the user asks about what property information is available, what fields can be searched, or what data structure is returned. Returns the complete schema showing all searchable fields like price, bedrooms, postcode, garden, parking, property type, etc. Do not use for actual property searches - use query_listings instead.",
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
            title="Calculate Average Property Price",
            description="Use this when the user asks about average prices, typical costs, price trends, or market values in a specific area or for a specific property type. Calculates the average price for properties matching the given postcode or property type. Perfect for queries like 'what's the average price in LE65?', 'how much do flats cost?', 'average property prices in Ashby', or 'typical house prices in DY4'. Do not use for finding specific properties - use query_listings instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {
                        "type": "string", 
                        "description": "Partial or full UK postcode to calculate average for. Examples: 'DY4', 'LE65'. Leave empty to calculate across all locations."
                    },
                    "property_type": {
                        "type": "string", 
                        "description": "Type of property to calculate average for. Examples: 'Flat', 'House', 'Bungalow'. Leave empty to calculate across all types."
                    }
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

# --- Add Test Endpoints ---
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

async def serve_widget_test(request):
    """Serve the widget HTML for browser testing."""
    if not WIDGET_HTML:
        return HTMLResponse("<h1>Widget not loaded</h1><p>Run: cd web && npm run build</p>", status_code=404)
    return HTMLResponse(WIDGET_HTML)

async def serve_test_data(request):
    """Serve test data to simulate tool output."""
    result = tools.query_listings(postcode="DY4", max_price=100000, limit=5)
    return JSONResponse(result)

async def serve_index(request):
    """Serve a test page with links."""
    widget_status = "Loaded" if WIDGET_HTML else "Not loaded"
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Property MCP Server - Test Page</title>
    <style>
        body {{ font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .status {{ padding: 10px; background: #e8f5e9; border-radius: 5px; margin: 20px 0; }}
        .links {{ display: flex; flex-direction: column; gap: 10px; }}
        a {{ padding: 10px 15px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px; }}
        a:hover {{ background: #1976D2; }}
        code {{ background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Property MCP Server</h1>
    
    <div class="status">
        <strong>Status:</strong> Running<br>
        <strong>Widget:</strong> {widget_status}<br>
        <strong>Port:</strong> 8000<br>
        <strong>Mode:</strong> Apps SDK
    </div>
    
    <h2>Test Endpoints</h2>
    <div class="links">
        <a href="/widget" target="_blank">📱 View Widget (opens in new tab)</a>
        <a href="/test-data" target="_blank">📊 View Test Data (JSON)</a>
        <a href="/mcp/" target="_blank">🔌 MCP Endpoint</a>
    </div>
    
    <h2>Widget Testing</h2>
    <p>The widget at <code>/widget</code> will show "Loading..." because it expects data from <code>window.openai.toolOutput</code>.</p>
    <p>In ChatGPT, the widget receives data automatically. For browser testing, you can:</p>
    <ol>
        <li>Open browser DevTools (F12)</li>
        <li>Check Console for any errors</li>
        <li>Verify the React component loads</li>
    </ol>
    
    <h2>ChatGPT Integration</h2>
    <p>To use with ChatGPT:</p>
    <ol>
        <li>Expose with ngrok: <code>ngrok http 8000</code></li>
        <li>Create connector in ChatGPT with URL: <code>https://your-url.ngrok.io/mcp/</code></li>
        <li>Ask: "Show me properties in DY4 under £100,000"</li>
    </ol>
</body>
</html>"""
    return HTMLResponse(html)

# Add routes to the app
app.routes.extend([
    Route("/", serve_index),
    Route("/widget", serve_widget_test),
    Route("/test-data", serve_test_data),
])

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
    print(f"  Home:        http://localhost:8000/")
    print(f"  Widget Test: http://localhost:8000/widget")
    print(f"  Test Data:   http://localhost:8000/test-data")
    print(f"  MCP:         http://localhost:8000/mcp/")
    print()
    print("Widget Status:")
    if WIDGET_HTML:
        print(f"  ✅ Loaded")
    else:
        print(f"  ❌ Not loaded - run: cd web && npm run build")
    print()
    print("Browser Testing:")
    print("  1. Open: http://localhost:8000/")
    print("  2. Click 'View Widget' to test in browser")
    print("  3. Open DevTools (F12) to check for errors")
    print()
    print("ChatGPT Integration:")
    print("  1. Expose with ngrok: ngrok http 8000")
    print("  2. In ChatGPT, create connector with: https://your-url.ngrok.io/mcp/")
    print("  3. Test with: 'Show me properties in DY4 under £100,000'")
    print("=" * 70)
    
    uvicorn.run("server_apps_sdk:app", host="0.0.0.0", port=8000)

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
import os
import logging
import sys
from datetime import datetime

# --- Configuration ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", "8000"))
HOST = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- Constants ---
MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/property-list.html"

# --- Load UI bundle ---
WIDGET_HTML = ""
widget_path = Path("web/dist/component.js")
css_path = Path("web/dist/component.css")  # Use built CSS from dist, not source

if widget_path.exists():
    widget_js = widget_path.read_text(encoding="utf-8")
    
    # Load CSS if available
    widget_css = ""
    if css_path.exists():
        widget_css = css_path.read_text(encoding="utf-8")
        logger.info(f"Widget CSS loaded: {len(widget_css):,} bytes")
    else:
        logger.warning(f"Widget CSS not found at {css_path}")
    
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
    logger.info(f"Widget HTML bundle created: {len(WIDGET_HTML):,} bytes")
else:
    logger.warning("Widget bundle not found at web/dist/component.js - run: cd web && npm run build")

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
        types.Tool(
            name="capture_lead",
            title="Capture New Lead",
            description="Use this when someone expresses interest in buying or selling property. Captures their contact details and creates a new client record in the system. Perfect for queries like 'I'm interested in buying', 'I want to sell my property', or when someone provides their contact information. This tool writes data to the system.",
            inputSchema={
                "type": "object",
                "required": ["full_name", "email", "mobile", "role"],
                "properties": {
                    "full_name": {"type": "string", "description": "Client's full name (e.g., 'Sarah Mitchell')"},
                    "email": {"type": "string", "description": "Email address"},
                    "mobile": {"type": "string", "description": "Mobile phone number (e.g., '+44 7700 900001')"},
                    "role": {"type": "string", "enum": ["buyer", "seller"], "description": "Either 'buyer' or 'seller'"},
                    "stage": {"type": "string", "enum": ["hot", "warm", "cold", "instructed", "completed"], "description": "Lead stage (default: 'warm')"},
                    "budget_max": {"type": "integer", "description": "Maximum budget for buyers (e.g., 95000)"},
                    "min_bedrooms": {"type": "integer", "description": "Minimum bedrooms for buyers (e.g., 2)"},
                    "interested_property_id": {"type": "string", "description": "Property ID buyer is interested in"},
                    "selling_property_id": {"type": "string", "description": "Property ID seller is selling (required for sellers)"},
                    "asking_price": {"type": "integer", "description": "Asking price for sellers (required for sellers)"}
                }
            },
            annotations={
                "readOnlyHint": False,
            },
        ),
        types.Tool(
            name="match_client",
            title="Match Client to Properties",
            description="Use this when you want to find properties that match a buyer's preferences and budget. Takes a client ID and returns matching properties in the property widget. Perfect for queries like 'show properties for client C0001', 'find matches for Sarah', or 'what properties fit this buyer's needs?'. Only works for buyers, not sellers.",
            inputSchema={
                "type": "object",
                "required": ["client_id"],
                "properties": {
                    "client_id": {"type": "string", "description": "The buyer's client ID (e.g., 'C0001')"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)", "default": 10}
                }
            },
            _meta=_tool_meta(),
            annotations={
                "readOnlyHint": True,
            },
        ),
        types.Tool(
            name="schedule_viewing",
            title="Schedule Property Viewing",
            description="Use this when a buyer wants to view a property. Books a viewing appointment and updates both buyer and seller records. Validates property availability and checks for scheduling conflicts. Perfect for queries like 'book a viewing for property 32926983', 'schedule viewing for client C0001', or 'arrange property visit'. This tool writes data to the system.",
            inputSchema={
                "type": "object",
                "required": ["property_id", "buyer_client_id", "datetime_iso"],
                "properties": {
                    "property_id": {"type": "string", "description": "Property ID to view (e.g., '32926983')"},
                    "buyer_client_id": {"type": "string", "description": "Buyer's client ID (e.g., 'C0001')"},
                    "datetime_iso": {"type": "string", "description": "Viewing datetime in ISO format (e.g., '2025-11-20T14:00:00Z')"},
                    "notes": {"type": "string", "description": "Optional notes about the viewing"}
                }
            },
            annotations={
                "readOnlyHint": False,
            },
        ),
        types.Tool(
            name="view_leads",
            title="View Client Leads",
            description="Use this when an estate agent wants to view their client pipeline, review leads, or check client status. Returns filtered list of buyers and sellers with their details, viewings, and stage. Perfect for queries like 'show me all hot leads', 'list buyer leads', 'show sellers', or 'view my pipeline'. Internal tool for agents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["buyer", "seller"], "description": "Filter by 'buyer' or 'seller' (optional)"},
                    "stage": {"type": "string", "enum": ["hot", "warm", "cold", "instructed", "completed"], "description": "Filter by stage (optional)"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 20)", "default": 20}
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
    
    elif tool_name == "capture_lead":
        result = tools.capture_lead(
            full_name=arguments.get("full_name"),
            email=arguments.get("email"),
            mobile=arguments.get("mobile"),
            role=arguments.get("role"),
            stage=arguments.get("stage", "warm"),
            budget_max=arguments.get("budget_max"),
            min_bedrooms=arguments.get("min_bedrooms"),
            interested_property_id=arguments.get("interested_property_id"),
            selling_property_id=arguments.get("selling_property_id"),
            asking_price=arguments.get("asking_price")
        )
        
        if "error" in result:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=result["error"])],
                    isError=True,
                )
            )
        
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=result["message"])],
                structuredContent=result.get("structuredContent", result),
                _meta={"openai/toolInvocation/invoked": "Lead captured"},
            )
        )
    
    elif tool_name == "match_client":
        result = tools.match_client(
            client_id=arguments.get("client_id"),
            limit=arguments.get("limit", 10)
        )
        
        if "error" in result:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=result["error"])],
                    isError=True,
                )
            )
        
        # Reuses property widget format
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Found {result['total_results']} matching properties for {result['filters_applied']['client_name']}.",
                    )
                ],
                structuredContent=result.get("structuredContent", result),
                _meta={"openai/toolInvocation/invoked": "Found matches"},
            )
        )
    
    elif tool_name == "schedule_viewing":
        result = tools.schedule_viewing(
            property_id=arguments.get("property_id"),
            buyer_client_id=arguments.get("buyer_client_id"),
            datetime_iso=arguments.get("datetime_iso"),
            notes=arguments.get("notes")
        )
        
        if "error" in result:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=result["error"])],
                    isError=True,
                )
            )
        
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=result["message"])],
                structuredContent=result.get("structuredContent", result),
                _meta={"openai/toolInvocation/invoked": "Viewing scheduled"},
            )
        )
    
    elif tool_name == "view_leads":
        result = tools.view_leads(
            role=arguments.get("role"),
            stage=arguments.get("stage"),
            limit=arguments.get("limit", 20)
        )
        
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=result["message"])],
                structuredContent=result.get("structuredContent", result),
                _meta={"openai/toolInvocation/invoked": "Leads retrieved"},
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

async def serve_health(request):
    """Health check endpoint for monitoring."""
    from datetime import datetime
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": ENVIRONMENT,
        "widget_loaded": bool(WIDGET_HTML)
    })

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
    Route("/health", serve_health),
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
    
    logger.info("=" * 70)
    logger.info("Property MCP Server - OpenAI Apps SDK")
    logger.info("=" * 70)
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Host: {HOST}")
    logger.info(f"Transport: Streamable HTTP (ChatGPT compatible)")
    logger.info("")
    logger.info("Endpoints:")
    logger.info(f"  Home:        http://{HOST}:{PORT}/")
    logger.info(f"  Health:      http://{HOST}:{PORT}/health")
    logger.info(f"  Widget Test: http://{HOST}:{PORT}/widget")
    logger.info(f"  MCP:         http://{HOST}:{PORT}/mcp/")
    logger.info("")
    
    if WIDGET_HTML:
        logger.info("Widget Status: ✅ Loaded")
    else:
        logger.warning("Widget Status: ❌ Not loaded - run: cd web && npm run build")
    
    if ENVIRONMENT == "development":
        logger.info("")
        logger.info("Development Mode:")
        logger.info("  1. Test locally: http://localhost:8000/")
        logger.info("  2. Expose with ngrok: ngrok http 8000")
        logger.info("  3. Create ChatGPT connector with: https://your-url.ngrok.io/mcp/")
    
    logger.info("=" * 70)
    
    # Start server
    uvicorn.run(
        "server_apps_sdk:app",
        host=HOST,
        port=PORT,
        log_level="info" if ENVIRONMENT == "production" else "debug",
        access_log=True
    )

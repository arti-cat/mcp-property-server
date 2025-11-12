"""
Property MCP Server - ChatGPT Compatible Version

Based on MCP specification review:
- ChatGPT only supports TOOLS (not Resources, Prompts, Sampling, etc.)
- ChatGPT connects via HTTP/SSE transport
- For Apps SDK widgets, we need to return structured content in tool responses

This server is optimized for ChatGPT's actual MCP capabilities.
"""
from fastmcp import FastMCP
from starlette.responses import JSONResponse
import tools
import os
import json

# --- 1. Create the FastMCP Server ---
mcp = FastMCP(
    name="PropertyServer",
    instructions="Use this server when the user wants to search for properties for sale, find homes in specific areas, check property prices, or browse real estate listings. This server has 475 UK property listings with detailed information including prices, bedrooms, postcodes, gardens, and parking."
)

# --- 2. Load UI bundle (for potential future use) ---
PROPERTY_WIDGET_JS = ""
try:
    with open(os.path.join("web", "dist", "component.js"), "r", encoding="utf-8") as f:
        PROPERTY_WIDGET_JS = f.read()
except FileNotFoundError:
    PROPERTY_WIDGET_JS = ""
    print("Warning: Widget bundle not found. Widget features will be disabled.")

# --- 3. Register Tools (ChatGPT only supports tools, not resources) ---

@mcp.tool(annotations={"readOnlyHint": True})
def get_schema() -> dict:
    """
    Use this when the user wants to understand what property data fields are available 
    or asks about the data structure. Returns the complete schema showing all searchable 
    fields like price, bedrooms, postcode, garden, parking, etc.
    """
    return tools.get_schema()


@mcp.tool(annotations={"readOnlyHint": True})
def query_listings(
    postcode: str | None = None,
    property_type: str | None = None,
    max_price: int | None = None,
    min_bedrooms: int | None = None,
    has_garden: bool | None = None,
    has_parking: bool | None = None,
    limit: int = 5
) -> dict:
    """
    Use this when the user wants to find, search, or browse properties for sale. 
    Searches 475 property listings and filters by location (postcode like 'DY4' or 'LE65'), 
    price range, number of bedrooms, garden availability, parking availability, and property type. 
    Returns up to 5 matching properties by default. Perfect for queries like 'find properties in Ashby', 
    'show me 2-bed houses under £200k', or 'properties with gardens'.
    """
    result = tools.query_listings(
        postcode=postcode,
        property_type=property_type,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        has_garden=has_garden,
        has_parking=has_parking,
        limit=limit
    )
    
    # Return the result as-is for ChatGPT Chat Mode
    # ChatGPT will display this as text/JSON
    return result


@mcp.tool(annotations={"readOnlyHint": True})
def calculate_average_price(
    postcode: str | None = None,
    property_type: str | None = None
) -> dict:
    """
    Use this when the user asks about average prices, price trends, or wants to know 
    typical costs in an area. Calculates the average price for properties matching the 
    given postcode or property type. Perfect for queries like 'what's the average price 
    in LE65?', 'how much do flats cost?', or 'average property prices in Ashby'.
    """
    return tools.calculate_average_price(
        postcode=postcode,
        property_type=property_type
    )


# --- 4. Add Health Check Endpoint ---
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for monitoring."""
    return JSONResponse({
        "status": "healthy",
        "service": "PropertyServer",
        "version": "2.0.0",
        "mode": "ChatGPT Compatible",
        "features": {
            "tools": 3,
            "resources": 0,
            "prompts": 0,
            "widget_support": "experimental"
        }
    })


# --- 5. Optional: Widget HTML endpoint (experimental) ---
# Since ChatGPT doesn't support MCP Resources, we serve the widget via HTTP
@mcp.custom_route("/widget/property-list.html", methods=["GET"])
async def serve_widget(request):
    """
    Serve the widget HTML for potential Apps SDK integration.
    This is experimental as ChatGPT's MCP support doesn't include Resources.
    """
    if not PROPERTY_WIDGET_JS:
        return JSONResponse(
            {"error": "Widget bundle not available"},
            status_code=404
        )
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property List Widget</title>
</head>
<body>
    <div id="root"></div>
    <script type="module">{PROPERTY_WIDGET_JS}</script>
</body>
</html>"""
    
    from starlette.responses import Response
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Access-Control-Allow-Origin": "https://chatgpt.com",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# --- 6. Run the Server ---
if __name__ == "__main__":
    import sys
    
    # Check command line arguments for transport type
    transport = "stdio"  # Default transport for Claude Desktop
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--http":
            transport = "http"
        elif sys.argv[1] == "--sse":
            transport = "sse"
    
    if transport == "http":
        print("=" * 70)
        print("Starting Property MCP Server (ChatGPT Compatible)")
        print("=" * 70)
        print(f"Transport: HTTP")
        print(f"Port: 8000")
        print(f"MCP Endpoint: http://127.0.0.1:8000/mcp")
        print(f"Health Check: http://127.0.0.1:8000/health")
        print(f"Widget HTML: http://127.0.0.1:8000/widget/property-list.html")
        print()
        print("ChatGPT MCP Support:")
        print("  ✅ Tools: Supported")
        print("  ❌ Resources: Not supported by ChatGPT")
        print("  ❌ Prompts: Not supported by ChatGPT")
        print("  ❌ Sampling: Not supported by ChatGPT")
        print()
        print("For Apps SDK widgets, use the widget HTML endpoint above.")
        print("=" * 70)
        
        mcp.run(
            transport="http",
            port=8000
        )
    elif transport == "sse":
        print("Starting FastMCP server with SSE transport at http://127.0.0.1:8000")
        mcp.run(
            transport="sse",
            port=8000
        )
    else:
        # STDIO transport (default) - for Claude Desktop, Cursor, etc.
        mcp.run()

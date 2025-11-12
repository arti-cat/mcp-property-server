"""
Property MCP Server using official MCP SDK for ChatGPT Apps SDK support.
This version properly supports the Apps SDK widget metadata structure.

Run with: python3 server_mcp_sdk.py --http
For STDIO: python3 server_mcp_sdk.py
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import sse_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types
import tools
import os
import asyncio
import sys
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
import uvicorn

# --- Load UI bundle ---
PROPERTY_WIDGET_JS = ""
try:
    with open(os.path.join("web", "dist", "component.js"), "r", encoding="utf-8") as f:
        PROPERTY_WIDGET_JS = f.read()
except FileNotFoundError:
    PROPERTY_WIDGET_JS = ""

# --- Create MCP Server ---
server = Server("PropertyServer")

# --- Register Resource with Apps SDK metadata ---
@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="ui://widget/property-list.html",
            name="Property List Widget",
            mimeType="text/html+skybridge",
            description="Interactive property listing widget"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content with Apps SDK metadata.
    
    For Apps SDK, the resource needs to include _meta fields in the response.
    The official MCP SDK will wrap this in the proper format.
    """
    if uri == "ui://widget/property-list.html":
        html_content = (
            "<div id=\"root\"></div>\n"
            + (f"<script type=\"module\">{PROPERTY_WIDGET_JS}</script>" if PROPERTY_WIDGET_JS else "")
        )
        
        # Return as text - the SDK handles the wrapping
        # Apps SDK metadata should be in the Resource descriptor above
        return html_content
    
    raise ValueError(f"Unknown resource: {uri}")

# --- Register Tools ---
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_schema",
            description="Use this when the user wants to understand what property data fields are available or asks about the data structure. Returns the complete schema showing all searchable fields like price, bedrooms, postcode, garden, parking, etc.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="query_listings",
            description="Use this when the user wants to find, search, or browse properties for sale. Searches 475 property listings and filters by location (postcode like 'DY4' or 'LE65'), price range, number of bedrooms, garden availability, parking availability, and property type. Returns up to 5 matching properties by default. Perfect for queries like 'find properties in Ashby', 'show me 2-bed houses under £200k', or 'properties with gardens'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {"type": "string", "description": "Partial or full UK postcode"},
                    "property_type": {"type": "string", "description": "Type of property"},
                    "max_price": {"type": "integer", "description": "Maximum price in GBP"},
                    "min_bedrooms": {"type": "integer", "description": "Minimum number of bedrooms"},
                    "has_garden": {"type": "boolean", "description": "Must have garden"},
                    "has_parking": {"type": "boolean", "description": "Must have parking"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                }
            }
        ),
        Tool(
            name="calculate_average_price",
            description="Use this when the user asks about average prices, price trends, or wants to know typical costs in an area. Calculates the average price for properties matching the given postcode or property type. Perfect for queries like 'what's the average price in LE65?', 'how much do flats cost?', or 'average property prices in Ashby'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "postcode": {"type": "string", "description": "Partial or full UK postcode"},
                    "property_type": {"type": "string", "description": "Type of property"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls with Apps SDK support.
    
    For Apps SDK widgets, we need to return content with proper structure.
    The official MCP SDK doesn't directly support structuredContent/_meta in the return type,
    so we may need to use a workaround or return JSON-encoded content.
    """
    if name == "get_schema":
        result = tools.get_schema()
        return [TextContent(type="text", text=str(result))]
    
    elif name == "query_listings":
        result = tools.query_listings(
            postcode=arguments.get("postcode"),
            property_type=arguments.get("property_type"),
            max_price=arguments.get("max_price"),
            min_bedrooms=arguments.get("min_bedrooms"),
            has_garden=arguments.get("has_garden"),
            has_parking=arguments.get("has_parking"),
            limit=arguments.get("limit", 5)
        )
        
        # For Apps SDK, we need to return structured content
        # The official SDK may not support this directly, so we return JSON
        import json
        return [TextContent(
            type="text", 
            text=json.dumps({
                "content": [{"type": "text", "text": f"Found {result['total_results']} properties."}],
                "structuredContent": result.get("structuredContent", result),
                "_meta": {}
            })
        )]
    
    elif name == "calculate_average_price":
        result = tools.calculate_average_price(
            postcode=arguments.get("postcode"),
            property_type=arguments.get("property_type")
        )
        return [TextContent(type="text", text=str(result))]
    
    raise ValueError(f"Unknown tool: {name}")

async def main_stdio():
    """Run the server with STDIO transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

async def main_sse():
    """Run the server with SSE transport for HTTP."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    
    sse = SseServerTransport("/messages")
    
    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
    
    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
    
    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )
    
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    # Check for --http flag
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        print("Starting MCP server with SSE transport at http://127.0.0.1:8000")
        asyncio.run(main_sse())
    else:
        # Default to STDIO
        asyncio.run(main_stdio())

from fastmcp import FastMCP
from starlette.responses import JSONResponse
import tools

# --- 1. Create the FastMCP Server ---
mcp = FastMCP(
    name="PropertyServer",
    instructions="A server for querying property listings."
)

# --- 2. Register Your Tools ---
@mcp.tool
def get_schema() -> dict:
    """Returns the data schema for property listings."""
    return tools.get_schema()

@mcp.tool
def query_listings(
    postcode: str | None = None,
    property_type: str | None = None,
    max_price: int | None = None,
    min_bedrooms: int | None = None,
    has_garden: bool | None = None,
    has_parking: bool | None = None,
    limit: int = 5
) -> list:
    """Searches and filters property listings based on specific criteria."""
    return tools.query_listings(
        postcode=postcode,
        property_type=property_type,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        has_garden=has_garden,
        has_parking=has_parking,
        limit=limit
    )

@mcp.tool
def calculate_average_price(
    postcode: str | None = None,
    property_type: str | None = None
) -> dict:
    """Calculates the average price for listings matching the given criteria."""
    return tools.calculate_average_price(
        postcode=postcode,
        property_type=property_type
    )


# --- 3. Add Health Check Endpoint ---
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for monitoring."""
    return JSONResponse({
        "status": "healthy",
        "service": "PropertyServer",
        "version": "1.0.0"
    })


# --- 4. Run the Server with Multiple Transport Options ---
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
        print("Starting FastMCP server with HTTP transport at http://127.0.0.1:8000")
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
        # No print statement needed as it interferes with STDIO communication
        mcp.run()
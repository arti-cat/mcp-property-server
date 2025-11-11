from fastmcp import FastMCP
from starlette.responses import JSONResponse
import tools

# --- 1. Create the FastMCP Server ---
mcp = FastMCP(
    name="PropertyServer",
    instructions="Use this server when the user wants to search for properties for sale, find homes in specific areas, check property prices, or browse real estate listings. This server has 475 UK property listings with detailed information including prices, bedrooms, postcodes, gardens, and parking."
)

# --- 2. Register Your Tools ---
@mcp.tool(annotations={"readOnlyHint": True})
def get_schema() -> dict:
    """Use this when the user wants to understand what property data fields are available or asks about the data structure. Returns the complete schema showing all searchable fields like price, bedrooms, postcode, garden, parking, etc."""
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
) -> list:
    """Use this when the user wants to find, search, or browse properties for sale. Searches 475 property listings and filters by location (postcode like 'DY4' or 'LE65'), price range, number of bedrooms, garden availability, parking availability, and property type. Returns up to 5 matching properties by default. Perfect for queries like 'find properties in Ashby', 'show me 2-bed houses under £200k', or 'properties with gardens'."""
    return tools.query_listings(
        postcode=postcode,
        property_type=property_type,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        has_garden=has_garden,
        has_parking=has_parking,
        limit=limit
    )

@mcp.tool(annotations={"readOnlyHint": True})
def calculate_average_price(
    postcode: str | None = None,
    property_type: str | None = None
) -> dict:
    """Use this when the user asks about average prices, price trends, or wants to know typical costs in an area. Calculates the average price for properties matching the given postcode or property type. Perfect for queries like 'what's the average price in LE65?', 'how much do flats cost?', or 'average property prices in Ashby'."""
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
"""
Test suite for PropertyServer using FastMCP Client.
Following the official FastMCP testing patterns.
"""
import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from server import mcp


@pytest.fixture
async def property_client():
    """Create a FastMCP client connected to the PropertyServer."""
    async with Client(transport=mcp) as client:
        yield client


async def test_list_tools(property_client: Client[FastMCPTransport]):
    """Test that all expected tools are registered."""
    tools = await property_client.list_tools()
    
    assert len(tools) == 3
    
    tool_names = [tool.name for tool in tools]
    assert "get_schema" in tool_names
    assert "query_listings" in tool_names
    assert "calculate_average_price" in tool_names


async def test_get_schema(property_client: Client[FastMCPTransport]):
    """Test the get_schema tool returns the correct schema."""
    result = await property_client.call_tool(
        name="get_schema",
        arguments={}
    )
    
    assert result.data is not None
    assert isinstance(result.data, dict)
    
    # Verify expected schema fields
    expected_fields = [
        "property_id", "price_amount", "bedrooms", "bathrooms",
        "property_type", "postcode", "garden", "parking", "status"
    ]
    
    for field in expected_fields:
        assert field in result.data


@pytest.mark.parametrize(
    "postcode, expected_min_count",
    [
        ("DY4 7LG", 1),  # Should have at least 1 property
        ("INVALID", 0),  # Invalid postcode should return 0
    ],
)
async def test_query_listings_by_postcode(
    postcode: str,
    expected_min_count: int,
    property_client: Client[FastMCPTransport],
):
    """Test querying listings by postcode."""
    result = await property_client.call_tool(
        name="query_listings",
        arguments={"postcode": postcode, "limit": 10}
    )
    
    assert result.data is not None
    assert isinstance(result.data, list)
    
    if expected_min_count > 0:
        assert len(result.data) >= expected_min_count
        # Verify all results match the postcode
        for listing in result.data:
            assert listing.get("postcode") == postcode
    else:
        assert len(result.data) == 0


@pytest.mark.parametrize(
    "max_price, min_bedrooms, limit",
    [
        (100000, 1, 5),
        (200000, 2, 3),
        (50000, 1, 10),
    ],
)
async def test_query_listings_with_filters(
    max_price: int,
    min_bedrooms: int,
    limit: int,
    property_client: Client[FastMCPTransport],
):
    """Test querying listings with various filters."""
    result = await property_client.call_tool(
        name="query_listings",
        arguments={
            "max_price": max_price,
            "min_bedrooms": min_bedrooms,
            "limit": limit
        }
    )
    
    assert result.data is not None
    assert isinstance(result.data, list)
    assert len(result.data) <= limit
    
    # Verify all results match the filters
    for listing in result.data:
        assert listing.get("price_amount", 0) <= max_price
        assert listing.get("bedrooms", 0) >= min_bedrooms


async def test_query_listings_with_boolean_filters(
    property_client: Client[FastMCPTransport],
):
    """Test querying listings with boolean filters."""
    result = await property_client.call_tool(
        name="query_listings",
        arguments={
            "has_garden": True,
            "has_parking": True,
            "limit": 5
        }
    )
    
    assert result.data is not None
    assert isinstance(result.data, list)
    
    # Verify all results have garden and parking
    for listing in result.data:
        assert listing.get("garden") is True
        assert listing.get("parking") is True


async def test_calculate_average_price_by_postcode(
    property_client: Client[FastMCPTransport],
):
    """Test calculating average price for a specific postcode."""
    result = await property_client.call_tool(
        name="calculate_average_price",
        arguments={"postcode": "DY4 7LG"}
    )
    
    assert result.data is not None
    assert isinstance(result.data, dict)
    
    # Check response structure
    assert "average_price" in result.data
    assert "count" in result.data
    assert "message" in result.data
    
    # If properties found, average should be positive
    if result.data["count"] > 0:
        assert result.data["average_price"] > 0
        assert isinstance(result.data["average_price"], (int, float))


async def test_calculate_average_price_by_property_type(
    property_client: Client[FastMCPTransport],
):
    """Test calculating average price for a specific property type."""
    result = await property_client.call_tool(
        name="calculate_average_price",
        arguments={"property_type": "Flat"}
    )
    
    assert result.data is not None
    assert isinstance(result.data, dict)
    assert "average_price" in result.data
    assert "count" in result.data


async def test_calculate_average_price_no_results(
    property_client: Client[FastMCPTransport],
):
    """Test calculating average price with no matching properties."""
    result = await property_client.call_tool(
        name="calculate_average_price",
        arguments={"postcode": "INVALID_POSTCODE"}
    )
    
    assert result.data is not None
    assert isinstance(result.data, dict)
    assert result.data["count"] == 0
    assert result.data["average_price"] is None
    assert "No listings found" in result.data["message"]


async def test_query_listings_limit_respected(
    property_client: Client[FastMCPTransport],
):
    """Test that the limit parameter is respected."""
    for limit in [1, 3, 5, 10]:
        result = await property_client.call_tool(
            name="query_listings",
            arguments={"limit": limit}
        )
        
        assert result.data is not None
        assert isinstance(result.data, list)
        assert len(result.data) <= limit


async def test_tool_descriptions(property_client: Client[FastMCPTransport]):
    """Test that all tools have proper descriptions."""
    tools = await property_client.list_tools()
    
    for tool in tools:
        assert tool.description is not None
        assert len(tool.description) > 0
        assert tool.inputSchema is not None

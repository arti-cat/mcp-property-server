#!/usr/bin/env python3
"""
Example MCP client for the Property Server.

This demonstrates how to use fastmcp.Client to interact with your own
or other MCP servers programmatically.
"""

import asyncio
from fastmcp import Client


async def main():
    # Connect to the local server
    async with Client("http://127.0.0.1:8000/mcp") as client:
        print("=== Connected to Property Server ===\n")
        
        # 1. List available tools
        print("Available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")
        print()
        
        # 2. Call a tool
        print("Calling query_listings for LE65 properties...")
        result = await client.call_tool(
            "query_listings",
            {"postcode": "LE65", "max_price": 300000, "limit": 3}
        )
        
        # Access the structured data
        data = result.data
        print(f"Found {data['total_results']} properties, showing {data['showing']}:\n")
        
        for prop in data['properties']:
            print(f"  📍 {prop['ld_name']}")
            print(f"     💰 {prop['price_text']} | 🛏️  {prop['bedrooms']} bed")
            print(f"     🏡 {prop['property_type']}")
            print()
        
        # 3. List resources
        print("Available resources:")
        resources = await client.list_resources()
        for resource in resources:
            print(f"  - {resource.uri} ({resource.mimeType})")
        print()
        
        # 4. Read a resource (the widget HTML)
        print("Reading widget resource...")
        contents = await client.read_resource("ui://widget/property-list.html")
        html = contents[0].text
        print(f"  Widget HTML: {len(html)} chars")
        print(f"  Contains React: {'React' in html or 'createElement' in html}")
        print()
        
        # 5. Calculate average price
        print("Calculating average price for LE65...")
        avg_result = await client.call_tool(
            "calculate_average_price",
            {"postcode": "LE65"}
        )
        avg_data = avg_result.data
        print(f"  Average: £{avg_data['average_price']:,.0f}")
        print(f"  Count: {avg_data['count']} properties")


if __name__ == "__main__":
    asyncio.run(main())

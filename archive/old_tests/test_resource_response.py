"""Test what FastMCP actually sends for resources."""
import asyncio
import json
from fastmcp.client import FastMCPClient

async def test():
    async with FastMCPClient("http://localhost:8000/mcp") as client:
        # List resources
        resources = await client.list_resources()
        print("=== RESOURCES LIST ===")
        print(json.dumps([r.model_dump() for r in resources], indent=2))
        
        # Read the widget resource
        if resources:
            uri = "ui://widget/property-list.html"
            print(f"\n=== READING RESOURCE: {uri} ===")
            try:
                content = await client.read_resource(uri)
                print(json.dumps([c.model_dump() for c in content], indent=2))
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())

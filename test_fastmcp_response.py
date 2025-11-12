"""
Test what FastMCP actually returns for Apps SDK format.
This will help us understand if FastMCP preserves the structuredContent and _meta fields.
"""
import asyncio
from fastmcp import FastMCP
import json

# Create test server
mcp = FastMCP("TestServer")

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openai/outputTemplate": "ui://widget/test.html",
    }
)
def test_tool() -> dict:
    """Test tool that returns Apps SDK format."""
    return {
        "content": [{"type": "text", "text": "Test message"}],
        "structuredContent": {"data": "test data"},
        "_meta": {"extra": "metadata"}
    }

@mcp.resource(
    uri="ui://widget/test.html",
    mime_type="text/html+skybridge",
    meta={
        "openai/widgetDescription": "Test widget",
        "openai/widgetPrefersBorder": True
    }
)
def test_widget():
    """Test widget resource."""
    return "<div>Test Widget</div>"

async def test_tool_response():
    """Test what the tool actually returns."""
    print("Testing FastMCP tool response format...")
    print("=" * 60)
    
    # Get the actual function
    print("\n1. Tool function test:")
    test_result = {
        "content": [{"type": "text", "text": "Test message"}],
        "structuredContent": {"data": "test data"},
        "_meta": {"extra": "metadata"}
    }
    print("Expected return format:")
    print(json.dumps(test_result, indent=2))
    
    # Try to get the tool's schema
    print("\n2. Tool registration:")
    tools = await mcp.list_tools()
    for tool in tools:
        if tool.name == "test_tool":
            print(f"  Name: {tool.name}")
            print(f"  Description: {tool.description}")
            if hasattr(tool, 'annotations'):
                print(f"  Annotations: {tool.annotations}")
    
    # Try to get the resource
    print("\n3. Resource registration:")
    try:
        resources = await mcp.get_resource_templates()
        print(f"  Found {len(resources)} resources")
        for res in resources:
            print(f"    - {res.uriTemplate if hasattr(res, 'uriTemplate') else res}")
    except Exception as e:
        print(f"  Error getting resources: {e}")
    
    print("\n" + "=" * 60)
    print("\nKey Question:")
    print("Does FastMCP preserve the {content, structuredContent, _meta} structure")
    print("or does it convert it to a different format?")
    print("\nTo test properly, we need to:")
    print("1. Start the server with --http")
    print("2. Use MCP Inspector or curl to call the tool")
    print("3. Check the actual JSON response")

if __name__ == "__main__":
    asyncio.run(test_tool_response())

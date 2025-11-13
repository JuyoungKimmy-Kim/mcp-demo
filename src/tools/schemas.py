"""Tool schemas for MCP Hub MCP Server"""

from mcp.types import Tool

TOOLS = [
    Tool(
        name="get_mcp_server_details",
        description="Get detailed information about a specific MCP server including tools, prompts, resources, and metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "integer",
                    "description": "The unique ID of the MCP server"
                }
            },
            "required": ["server_id"]
        }
    )
]

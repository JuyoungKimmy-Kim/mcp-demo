"""Tool handlers for MCP Hub MCP Server"""
from typing import Any
from mcp.types import TextContent


async def handle_tool_call(name: str, arguments: Any, api_client) -> list[TextContent]:
    """Handle tool calls from MCP clients"""

    if name == "list_mcp_servers":
        result = await api_client.list_servers(
            sort=arguments.get("sort", "favorites"),
            order=arguments.get("order", "desc"),
            limit=arguments.get("limit", 20)
        )
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

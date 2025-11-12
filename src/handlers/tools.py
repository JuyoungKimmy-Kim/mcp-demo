"""Tool handlers for MCP Hub MCP Server"""
from typing import Any, Dict
from mcp.types import TextContent


def format_server_details(data: Dict[str, Any]) -> str:
    """Format server details data into readable text"""
    if not data:
        return "Server not found"

    lines = []
    lines.append(f"📦 {data.get('name', 'Unknown')}")
    lines.append(f"   ID: {data.get('id')}")
    lines.append(f"   Description: {data.get('description', 'No description')}")
    lines.append(f"   Author: {data.get('author', 'Unknown')}")
    lines.append(f"   ⭐ Favorites: {data.get('favorites_count', 0)}")

    if data.get('repository_url'):
        lines.append(f"   🔗 Repository: {data['repository_url']}")

    if data.get('created_at'):
        lines.append(f"   📅 Created: {data['created_at']}")

    return "\n".join(lines)


async def handle_tool_call(name: str, arguments: Any, api_client) -> list[TextContent]:
    """Handle tool calls from MCP clients"""

    if name == "get_mcp_server_details":
        server_id = arguments.get("server_id")
        data = await api_client.get_server_details(server_id)
        formatted_text = format_server_details(data)
        return [TextContent(type="text", text=formatted_text)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

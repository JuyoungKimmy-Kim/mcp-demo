"""Tool handlers for MCP Hub MCP Server"""

from typing import Any, Dict
from mcp.types import TextContent


async def handle_tool_call(name: str, arguments: Dict[str, Any], api_client) -> list[TextContent]:
    """Handle tool calls from MCP clients"""
    if name == "get_mcp_server_details":
        server_id = arguments.get("server_id")
        data = await api_client.get_server_details(server_id)
        formatted_text = format_server_details(data)
        return [TextContent(type="text", text=formatted_text)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def format_server_details(server: Dict[str, Any]) -> str:
    """Format server details response"""
    result = f"=== {server.get('name', 'Unknown')} ===\n\n"
    result += f"ID: {server.get('id')}\n"
    result += f"Description: {server.get('description', 'N/A')}\n"
    result += f"GitHub: {server.get('github_link', 'N/A')}\n"
    result += f"Protocol: {server.get('protocol', 'N/A')}\n"
    result += f"Status: {server.get('status', 'N/A')}\n"
    result += f"Favorites: {server.get('favorites_count', 0)}\n"

    tags = server.get('tags', [])
    if tags:
        tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags]
        result += f"Tags: {', '.join(tag_names)}\n"

    tools = server.get('tools', [])
    if tools:
        result += f"\n--- Tools ({len(tools)}) ---\n"
        for tool in tools:
            result += f"  • {tool.get('name', 'Unknown')}\n"
            if tool.get('description'):
                result += f"    {tool['description']}\n"

    if server.get('created_at'):
        result += f"\nCreated: {server['created_at']}\n"

    return result

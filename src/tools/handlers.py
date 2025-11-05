"""Tool handlers for MCP Hub MCP Server"""

import json
import logging
from typing import Any, Dict, Callable
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class ToolHandler:
    """Handler for tool execution"""

    def __init__(self, api_client):
        """Initialize handler with API client

        Args:
            api_client: APIClient instance for making API requests
        """
        self.api_client = api_client

        # Tool handler mapping
        self._handlers: Dict[str, Callable] = {
            "search_mcp_servers": self._search_servers,
            "list_mcp_servers": self._list_servers,
            "get_mcp_server_details": self._get_server_details,
            "get_top_servers": self._get_top_servers,
            "get_top_contributors": self._get_top_contributors,
        }

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle tool calls from MCP clients

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        handler = self._handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        try:
            result = await handler(arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _search_servers(self, arguments: Dict[str, Any]) -> str:
        """Search MCP servers by keyword"""
        keyword = arguments.get("keyword")
        data = await self.api_client.search_servers(keyword=keyword)
        return self._format_server_list(data, f"Search results for '{keyword}'")

    async def _list_servers(self, arguments: Dict[str, Any]) -> str:
        """List MCP servers with pagination"""
        sort = arguments.get("sort", "favorites")
        order = arguments.get("order", "desc")
        limit = arguments.get("limit", 20)
        offset = arguments.get("offset", 0)

        data = await self.api_client.list_servers(
            sort=sort,
            order=order,
            limit=limit,
            offset=offset
        )
        return self._format_server_list(data, f"MCP Servers (sort={sort}, limit={limit})")

    async def _get_server_details(self, arguments: Dict[str, Any]) -> str:
        """Get server details"""
        server_id = arguments.get("server_id")
        if not server_id:
            return "Error: server_id is required"

        data = await self.api_client.get_server_details(server_id)
        return self._format_server_details(data)

    async def _get_top_servers(self, arguments: Dict[str, Any]) -> str:
        """Get top servers"""
        limit = arguments.get("limit", 3)
        sort = arguments.get("sort", "favorites")

        data = await self.api_client.get_top_servers(limit=limit, sort=sort)
        sort_label = "Most Popular" if sort == "favorites" else "Latest"
        return self._format_server_list(data, f"{sort_label} Servers (Top {limit})")

    async def _get_top_contributors(self, arguments: Dict[str, Any]) -> str:
        """Get top contributors"""
        limit = arguments.get("limit", 3)
        data = await self.api_client.get_top_contributors(limit=limit)
        return self._format_contributors(data, limit)

    def _format_server_list(self, data: Dict[str, Any], title: str) -> str:
        """Format server list response"""
        servers = data if isinstance(data, list) else data.get("servers", [])

        if not servers:
            return f"{title}\n\nNo servers found."

        result = f"{title}\n{'=' * 60}\n\n"

        for idx, server in enumerate(servers, 1):
            result += f"{idx}. {server.get('name', 'Unknown')}\n"
            result += f"   ID: {server.get('id')}\n"

            desc = server.get('description', '')
            if desc:
                result += f"   Description: {desc[:100]}{'...' if len(desc) > 100 else ''}\n"

            result += f"   GitHub: {server.get('github_link', 'N/A')}\n"
            result += f"   Favorites: {server.get('favorites_count', 0)}\n"

            tags = server.get('tags', [])
            if tags:
                tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags]
                result += f"   Tags: {', '.join(tag_names)}\n"

            result += "\n"

        return result

    def _format_server_details(self, server: Dict[str, Any]) -> str:
        """Format server details response"""
        result = f"=== {server.get('name', 'Unknown')} ===\n\n"
        result += f"ID: {server.get('id')}\n"
        result += f"Description: {server.get('description', 'N/A')}\n"
        result += f"GitHub: {server.get('github_link', 'N/A')}\n"
        result += f"Protocol: {server.get('protocol', 'N/A')}\n"
        result += f"Status: {server.get('status', 'N/A')}\n"
        result += f"Favorites: {server.get('favorites_count', 0)}\n"

        # Tags
        tags = server.get('tags', [])
        if tags:
            tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags]
            result += f"Tags: {', '.join(tag_names)}\n"

        # Tools
        tools = server.get('tools', [])
        if tools:
            result += f"\n--- Tools ({len(tools)}) ---\n"
            for tool in tools:
                result += f"  • {tool.get('name', 'Unknown')}\n"
                if tool.get('description'):
                    result += f"    {tool['description']}\n"

        # Additional metadata
        if server.get('created_at'):
            result += f"\nCreated: {server['created_at']}\n"

        return result

    def _format_contributors(self, data: Dict[str, Any], limit: int) -> str:
        """Format contributors response"""
        users = data if isinstance(data, list) else data.get("users", data.get("top_users", []))

        if not users:
            return f"Top Contributors (Top {limit})\n\nNo contributors found."

        result = f"Top Contributors (Top {limit})\n{'=' * 60}\n\n"

        for idx, user in enumerate(users, 1):
            username = user.get("username", user.get("user_name", "Unknown"))
            server_count = user.get("server_count", user.get("count", 0))

            result += f"{idx}. {username}\n"
            result += f"   Servers: {server_count}\n\n"

        return result

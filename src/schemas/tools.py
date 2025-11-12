"""Tool definitions for MCP Hub MCP Server"""
from mcp.types import Tool

TOOLS = [
    Tool(
        name="list_mcp_servers",
        description="List MCP servers with sorting and pagination",
        inputSchema={
            "type": "object",
            "properties": {
                "sort": {
                    "type": "string",
                    "enum": ["favorites", "created_at"],
                    "description": "Sort by favorites or creation date",
                    "default": "favorites"
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order",
                    "default": "desc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results",
                    "default": 20
                }
            }
        }
    ),
]

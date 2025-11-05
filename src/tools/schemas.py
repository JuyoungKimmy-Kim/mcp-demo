"""Tool schemas for MCP Hub MCP Server"""

from mcp.types import Tool

TOOLS = [
    Tool(
        name="search_mcp_servers",
        description="Search for MCP servers by keyword. Returns matching servers with basic information.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword to match against server name or description"
                }
            }
        }
    ),
    Tool(
        name="list_mcp_servers",
        description="List MCP servers with pagination and sorting options. Use this to browse the marketplace.",
        inputSchema={
            "type": "object",
            "properties": {
                "sort": {
                    "type": "string",
                    "enum": ["favorites", "created_at"],
                    "description": "Sort field: 'favorites' (most popular) or 'created_at' (newest)",
                    "default": "favorites"
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order: 'asc' or 'desc'",
                    "default": "desc"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return (default: 20)",
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of results to skip (default: 0)",
                    "default": 0
                }
            }
        }
    ),
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
    ),
    Tool(
        name="get_top_servers",
        description="Get top MCP servers by popularity (favorites) or recency (created_at).",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of top servers to return (default: 3)",
                    "default": 3
                },
                "sort": {
                    "type": "string",
                    "enum": ["favorites", "created_at"],
                    "description": "Sort field: 'favorites' (most popular) or 'created_at' (newest)",
                    "default": "favorites"
                }
            }
        }
    ),
    Tool(
        name="get_top_contributors",
        description="Get top contributors (users with most MCP servers registered).",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of top contributors to return (default: 3)",
                    "default": 3
                }
            }
        }
    )
]

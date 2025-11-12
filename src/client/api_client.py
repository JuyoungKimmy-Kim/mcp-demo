"""API client for MCP Hub"""
from typing import Optional, Dict, Any
import httpx


class APIClient:
    """Client for accessing MCP Hub REST API"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=False  # SSL 에러 방지 (사내 서비스용)
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.api_base_url}{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def list_servers(
        self,
        sort: str = "favorites",
        order: str = "desc",
        limit: int = 20
    ) -> str:
        """List MCP servers with sorting"""
        params = {
            "status": "approved",
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": 0
        }
        data = await self._get("/api/v1/mcp-servers/", params)

        servers = data.get("items", [])
        total = data.get("total", 0)

        result = f"Total servers: {total}\n"
        result += f"Showing {len(servers)} servers (sorted by {sort}, {order}):\n\n"

        for server in servers:
            result += f"ID: {server['id']}\n"
            result += f"Name: {server['name']}\n"
            result += f"Description: {server.get('description', 'N/A')}\n"
            result += f"Favorites: {server.get('favorites_count', 0)}\n"
            result += "-" * 60 + "\n\n"

        return result

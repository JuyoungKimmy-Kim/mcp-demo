"""API client for MCP Hub"""
from typing import Dict, Any
import httpx


class APIClient:
    """Client for accessing MCP Hub REST API"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=False
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.api_base_url}{endpoint}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_server_details(self, server_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific MCP server"""
        return await self._get(f"/api/v1/mcp-servers/{server_id}")

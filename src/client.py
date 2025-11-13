"""HTTP API client for MCP Hub backend"""

import os
from typing import Any, Dict
import httpx


class APIClient:
    """Client for MCP Hub API"""

    def __init__(self, base_url: str = None):
        """Initialize API client"""
        self.base_url = base_url or os.getenv("MCP_HUB_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_server_details(self, server_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific server"""
        url = f"{self.base_url}/api/v1/mcp-servers/{server_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

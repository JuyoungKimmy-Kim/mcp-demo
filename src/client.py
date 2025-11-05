"""HTTP API client for MCP Hub backend"""

import logging
from typing import Any, Dict, Optional
import httpx

from .config import config

logger = logging.getLogger(__name__)


class APIClient:
    """Client for MCP Hub API"""

    def __init__(self):
        """Initialize API client with configuration"""
        self.base_url = config.api_base_url
        self.client = httpx.AsyncClient(
            timeout=config.api_timeout,
            verify=config.verify_ssl,
            follow_redirects=True
        )

        if not config.verify_ssl:
            logger.warning("SSL certificate verification is disabled")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.debug(f"GET {url} with params: {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def _post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.debug(f"POST {url} with data: {json_data}")
            response = await self.client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def search_servers(self, keyword: Optional[str] = None, tags: Optional[list[str]] = None) -> Dict[str, Any]:
        """Search MCP servers by keyword and/or tags"""
        json_data = {"status": "approved"}
        if keyword:
            json_data["keyword"] = keyword
        if tags:
            json_data["tags"] = tags
        return await self._post("/mcp-servers/search", json_data)

    async def list_servers(
        self,
        sort: str = "favorites",
        order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List MCP servers with pagination and sorting"""
        params = {
            "status": "approved",
            "sort": sort,
            "order": order,
            "limit": limit,
            "offset": offset
        }
        return await self._get("/mcp-servers/", params)

    async def get_server_details(self, server_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific server"""
        return await self._get(f"/mcp-servers/{server_id}")

    async def get_top_servers(self, limit: int = 3, sort: str = "favorites") -> Dict[str, Any]:
        """Get top servers by favorites or created_at"""
        params = {
            "status": "approved",
            "sort": sort,
            "order": "desc",
            "limit": limit,
            "offset": 0
        }
        return await self._get("/mcp-servers/", params)

    async def get_top_contributors(self, limit: int = 3) -> Dict[str, Any]:
        """Get top contributors"""
        params = {"limit": limit}
        return await self._get("/mcp-servers/top-users", params)

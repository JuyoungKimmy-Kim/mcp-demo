"""Integration tests for API client (requires running backend)"""

import pytest
from src.client import APIClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestAPIClientIntegration:
    """Integration tests for API client (requires backend at http://localhost:8000)"""

    async def test_client_initialization(self):
        """Test API client initialization"""
        client = APIClient()
        assert client is not None
        assert client.base_url == "http://localhost:8000/api/v1"
        await client.close()

    async def test_search_servers(self):
        """Test search_servers method"""
        client = APIClient()
        try:
            result = await client.search_servers(keyword="github")
            assert result is not None
            assert isinstance(result, (dict, list))
        finally:
            await client.close()

    async def test_list_servers(self):
        """Test list_servers method"""
        client = APIClient()
        try:
            result = await client.list_servers(limit=5, sort="favorites")
            assert result is not None
            assert isinstance(result, (dict, list))
        finally:
            await client.close()

    async def test_get_server_details(self):
        """Test get_server_details method"""
        client = APIClient()
        try:
            result = await client.get_server_details(server_id=5)
            assert result is not None
            assert isinstance(result, dict)
        finally:
            await client.close()

    async def test_get_top_servers(self):
        """Test get_top_servers method"""
        client = APIClient()
        try:
            result = await client.get_top_servers(limit=3, sort="favorites")
            assert result is not None
            assert isinstance(result, (dict, list))
        finally:
            await client.close()

    async def test_get_top_contributors(self):
        """Test get_top_contributors method"""
        client = APIClient()
        try:
            result = await client.get_top_contributors(limit=3)
            assert result is not None
            assert isinstance(result, (dict, list))
        finally:
            await client.close()

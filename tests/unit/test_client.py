"""Unit tests for API client with mocks"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.client import APIClient


@pytest.mark.asyncio
class TestAPIClientUnit:
    """Unit tests for API client (with mocks)"""

    async def test_search_servers_mock(self, mocker):
        """Test search_servers with mock"""
        client = APIClient()

        # Mock the _post method
        mock_response = {"servers": [{"id": 1, "name": "test"}]}
        mocker.patch.object(client, '_post', return_value=mock_response)

        result = await client.search_servers(keyword="github")

        assert result == mock_response
        client._post.assert_called_once_with(
            "/mcp-servers/search",
            {"status": "approved", "keyword": "github"}
        )
        await client.close()

    async def test_list_servers_mock(self, mocker):
        """Test list_servers with mock"""
        client = APIClient()

        mock_response = {"servers": [{"id": 1, "name": "test"}]}
        mocker.patch.object(client, '_get', return_value=mock_response)

        result = await client.list_servers(limit=5, sort="favorites")

        assert result == mock_response
        client._get.assert_called_once_with(
            "/mcp-servers/",
            {"status": "approved", "sort": "favorites", "order": "desc", "limit": 5, "offset": 0}
        )
        await client.close()

    async def test_get_server_details_mock(self, mocker):
        """Test get_server_details with mock"""
        client = APIClient()

        mock_response = {"id": 5, "name": "github mcp"}
        mocker.patch.object(client, '_get', return_value=mock_response)

        result = await client.get_server_details(server_id=5)

        assert result == mock_response
        client._get.assert_called_once_with("/mcp-servers/5")
        await client.close()

    async def test_get_top_servers_mock(self, mocker):
        """Test get_top_servers with mock"""
        client = APIClient()

        mock_response = {"servers": [{"id": 1, "name": "top server"}]}
        mocker.patch.object(client, '_get', return_value=mock_response)

        result = await client.get_top_servers(limit=3, sort="favorites")

        assert result == mock_response
        client._get.assert_called_once_with(
            "/mcp-servers/",
            {"status": "approved", "sort": "favorites", "order": "desc", "limit": 3, "offset": 0}
        )
        await client.close()

    async def test_get_top_contributors_mock(self, mocker):
        """Test get_top_contributors with mock"""
        client = APIClient()

        mock_response = {"users": [{"username": "admin", "server_count": 5}]}
        mocker.patch.object(client, '_get', return_value=mock_response)

        result = await client.get_top_contributors(limit=3)

        assert result == mock_response
        client._get.assert_called_once_with("/mcp-servers/top-users", {"limit": 3})
        await client.close()

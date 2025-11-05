"""Unit tests for tool handlers"""

import pytest
from mcp.types import TextContent
from src.tools.handlers import ToolHandler


@pytest.mark.asyncio
class TestToolHandlerUnit:
    """Unit tests for ToolHandler"""

    async def test_handler_initialization(self):
        """Test handler initialization"""
        mock_client = None
        handler = ToolHandler(mock_client)
        assert handler is not None
        assert handler.api_client is None

    async def test_unknown_tool(self, mocker):
        """Test handling unknown tool"""
        mock_client = mocker.MagicMock()
        handler = ToolHandler(mock_client)

        result = await handler.handle_tool_call("unknown_tool", {})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown tool" in result[0].text

    async def test_search_servers_handler(self, mocker):
        """Test search_servers handler"""
        mock_client = mocker.AsyncMock()
        mock_client.search_servers.return_value = {"servers": [{"id": 1, "name": "test"}]}

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call("search_mcp_servers", {"keyword": "github"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        mock_client.search_servers.assert_called_once_with(keyword="github")

    async def test_list_servers_handler(self, mocker):
        """Test list_servers handler"""
        mock_client = mocker.AsyncMock()
        mock_client.list_servers.return_value = {"servers": [{"id": 1, "name": "test"}]}

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call(
            "list_mcp_servers",
            {"limit": 5, "sort": "favorites"}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.list_servers.assert_called_once()

    async def test_get_server_details_handler(self, mocker):
        """Test get_server_details handler"""
        mock_client = mocker.AsyncMock()
        mock_client.get_server_details.return_value = {"id": 5, "name": "github mcp"}

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call(
            "get_mcp_server_details",
            {"server_id": 5}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.get_server_details.assert_called_once_with(5)

    async def test_get_top_servers_handler(self, mocker):
        """Test get_top_servers handler"""
        mock_client = mocker.AsyncMock()
        mock_client.get_top_servers.return_value = {"servers": [{"id": 1}]}

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call(
            "get_top_servers",
            {"limit": 3, "sort": "favorites"}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.get_top_servers.assert_called_once_with(limit=3, sort="favorites")

    async def test_get_top_contributors_handler(self, mocker):
        """Test get_top_contributors handler"""
        mock_client = mocker.AsyncMock()
        mock_client.get_top_contributors.return_value = {"users": [{"username": "admin"}]}

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call(
            "get_top_contributors",
            {"limit": 3}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        mock_client.get_top_contributors.assert_called_once_with(limit=3)

    async def test_handler_error_handling(self, mocker):
        """Test handler error handling"""
        mock_client = mocker.AsyncMock()
        mock_client.search_servers.side_effect = Exception("API Error")

        handler = ToolHandler(mock_client)
        result = await handler.handle_tool_call("search_mcp_servers", {"keyword": "test"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error" in result[0].text

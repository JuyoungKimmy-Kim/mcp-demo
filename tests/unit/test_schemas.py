"""Unit tests for tool schemas"""

import pytest
from mcp.types import Tool
from src.tools.schemas import TOOLS


class TestToolSchemas:
    """Test tool schema definitions"""

    def test_tools_list_exists(self):
        """Test TOOLS list exists and is not empty"""
        assert TOOLS is not None
        assert isinstance(TOOLS, list)
        assert len(TOOLS) == 5

    def test_all_tools_are_tool_objects(self):
        """Test all items in TOOLS are Tool objects"""
        for tool in TOOLS:
            assert isinstance(tool, Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')

    def test_tool_names_are_valid(self):
        """Test all tool names are non-empty strings"""
        for tool in TOOLS:
            assert isinstance(tool.name, str)
            assert len(tool.name) > 0
            assert tool.name.strip() == tool.name  # No leading/trailing whitespace

    def test_all_tools_have_descriptions(self):
        """Test all tools have non-empty descriptions"""
        for tool in TOOLS:
            assert tool.description is not None
            assert isinstance(tool.description, str)
            assert len(tool.description) > 0

    def test_all_tools_have_valid_input_schemas(self):
        """Test all tools have valid input schemas"""
        for tool in TOOLS:
            assert tool.inputSchema is not None
            assert isinstance(tool.inputSchema, dict)
            assert "type" in tool.inputSchema
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema

    def test_no_duplicate_tool_names(self):
        """Test there are no duplicate tool names"""
        tool_names = [tool.name for tool in TOOLS]
        assert len(tool_names) == len(set(tool_names))

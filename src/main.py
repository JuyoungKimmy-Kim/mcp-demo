#!/usr/bin/env python3
"""MCP Hub MCP Server - Main Entry Point"""
import asyncio
import os
from mcp.server import Server

from client.api_client import APIClient
from schemas.tools import TOOLS
from handlers.tools import handle_tool_call
from transport.http import run_http_transport


async def main():
    """Main function"""
    api_base_url = os.getenv("MCP_HUB_URL", "http://localhost:8000")
    api_client = APIClient(api_base_url)
    app = Server("mcp-hub-mcp")

    @app.list_tools()
    async def list_tools():
        """Return list of available tools"""
        return TOOLS

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""
        return await handle_tool_call(name, arguments, api_client)

    await run_http_transport(app, api_client)


if __name__ == "__main__":
    asyncio.run(main())

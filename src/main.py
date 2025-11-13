#!/usr/bin/env python3
"""MCP Hub MCP Server - Simple Example"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from client import APIClient
from tools.schemas import TOOLS
from tools.handlers import handle_tool_call
from transport import run_http_transport

app = Server("mcp-hub-mcp")
api_client: APIClient | None = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    return await handle_tool_call(name, arguments, api_client)


async def main():
    """Main entry point"""
    global api_client

    api_client = APIClient()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10004"))

    await run_http_transport(app, host=host, port=port)
    await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())

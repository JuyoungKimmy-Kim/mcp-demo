#!/usr/bin/env python3
"""
MCP Hub MCP Server
Provides tools to query the MCP Hub database
"""

import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

from .config import config
from .client import APIClient
from .tools.schemas import TOOLS
from .tools.handlers import ToolHandler
from .transport import run_http_transport, run_stdio_transport

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("mcp-hub-mcp")

# Global instances
api_client: APIClient | None = None
tool_handler: ToolHandler | None = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    global tool_handler

    if tool_handler is None:
        return [TextContent(type="text", text="Error: Tool handler not initialized")]

    return await tool_handler.handle_tool_call(name, arguments)


async def main():
    """Main entry point"""
    global api_client, tool_handler

    # Initialize API client
    api_client = APIClient()
    logger.info(f"API client initialized (base URL: {api_client.base_url})")

    # Initialize tool handler
    tool_handler = ToolHandler(api_client)
    logger.info("Tool handler initialized")

    # Determine transport mode
    transport_mode = os.getenv("TRANSPORT_MODE", "http").lower()

    try:
        if transport_mode == "stdio":
            await run_stdio_transport(app)
        else:
            # Default to HTTP
            await run_http_transport(
                app,
                host=config.server_host,
                port=config.server_port
            )
    finally:
        # Cleanup
        if api_client:
            await api_client.close()
            logger.info("API client closed")


if __name__ == "__main__":
    asyncio.run(main())

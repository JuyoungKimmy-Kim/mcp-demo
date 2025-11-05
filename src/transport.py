"""HTTP transport for MCP server"""

import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


async def run_http_transport(app: Server, host: str = "0.0.0.0", port: int = 8080):
    """Run MCP server with HTTP (SSE) transport

    Args:
        app: MCP Server instance
        host: Host to bind to
        port: Port to bind to
    """
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )

    import uvicorn
    logger.info(f"Starting HTTP transport on {host}:{port}")
    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def run_stdio_transport(app: Server):
    """Run MCP server with stdio transport

    Args:
        app: MCP Server instance
    """
    logger.info("Starting stdio transport")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

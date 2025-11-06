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

    sse = SseServerTransport("/messages")

    # Main ASGI app that routes requests
    async def asgi_app(scope, receive, send):
        """Main ASGI app for routing"""
        if scope["type"] == "http":
            path = scope["path"]

            if path == "/sse":
                # Handle SSE endpoint
                async with sse.connect_sse(scope, receive, send) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )
            elif path == "/messages":
                # Handle messages endpoint
                await sse.handle_post_message(scope, receive, send)
            else:
                # 404 for other paths
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })

    import uvicorn
    logger.info(f"Starting HTTP transport on {host}:{port}")
    config = uvicorn.Config(asgi_app, host=host, port=port, log_level="info")
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

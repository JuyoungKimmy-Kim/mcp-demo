"""HTTP transport for MCP server"""

from mcp.server import Server
from mcp.server.sse import SseServerTransport
import uvicorn


async def run_http_transport(app: Server, host: str = "0.0.0.0", port: int = 10004):
    """Run MCP server with HTTP (SSE) transport"""
    sse = SseServerTransport("/messages")

    async def asgi_app(scope, receive, send):
        """Main ASGI app for routing"""
        if scope["type"] == "http":
            path = scope["path"]

            if path == "/sse":
                async with sse.connect_sse(scope, receive, send) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )
            elif path == "/messages":
                await sse.handle_post_message(scope, receive, send)
            elif path == "/health":
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"status":"healthy","service":"mcp-hub-mcp"}',
                })
            else:
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })

    config = uvicorn.Config(asgi_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

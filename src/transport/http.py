"""HTTP/SSE transport for MCP Hub MCP Server"""
import os
from mcp.server.sse import SseServerTransport
import uvicorn


async def run_http_transport(app, api_client) -> None:
    """Run server with HTTP/SSE transport"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10004"))

    # SSE Transport 생성
    sse = SseServerTransport("/messages")

    # ASGI app
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
            elif path == "/health":
                # Health check
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

    try:
        config = uvicorn.Config(asgi_app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        # 종료 시 정리
        await api_client.close()

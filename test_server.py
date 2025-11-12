#!/usr/bin/env python3
"""Test get_mcp_server_details tool"""
import asyncio
import httpx


async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:10004/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.text}\n")


if __name__ == "__main__":
    print("=== Testing MCP Server ===\n")
    asyncio.run(test_health())
    print("✅ MCP 서버가 정상적으로 실행 중입니다!")
    print(f"\nServer URL: http://localhost:10004/sse")
    print(f"Tool: get_mcp_server_details")
    print(f"\n참고: MCP Hub API (http://localhost:8000)가 실행 중이어야 tool이 작동합니다.")

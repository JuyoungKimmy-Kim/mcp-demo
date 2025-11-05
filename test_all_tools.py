#!/usr/bin/env python3
"""Test all 5 MCP tools"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_all_tools():
    """Test all 5 MCP tools"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.main"],
        env={"TRANSPORT_MODE": "stdio"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n" + "="*60)
            print("MCP Hub MCP Server - Testing All Tools")
            print("="*60)

            # Test 1: search_mcp_servers
            print("\n[1/5] Testing: search_mcp_servers")
            print("-"*60)
            try:
                result = await session.call_tool(
                    "search_mcp_servers",
                    arguments={"keyword": "github"}
                )
                output = result.content[0].text
                print(output[:300] + "..." if len(output) > 300 else output)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")

            # Test 2: list_mcp_servers
            print("\n[2/5] Testing: list_mcp_servers")
            print("-"*60)
            try:
                result = await session.call_tool(
                    "list_mcp_servers",
                    arguments={"limit": 3, "sort": "created_at", "order": "desc"}
                )
                output = result.content[0].text
                print(output[:300] + "..." if len(output) > 300 else output)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")

            # Test 3: get_mcp_server_details
            print("\n[3/5] Testing: get_mcp_server_details")
            print("-"*60)
            try:
                result = await session.call_tool(
                    "get_mcp_server_details",
                    arguments={"server_id": 5}
                )
                output = result.content[0].text
                print(output[:400] + "..." if len(output) > 400 else output)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")

            # Test 4: get_top_servers (favorites)
            print("\n[4/5] Testing: get_top_servers (sort=favorites)")
            print("-"*60)
            try:
                result = await session.call_tool(
                    "get_top_servers",
                    arguments={"limit": 3, "sort": "favorites"}
                )
                output = result.content[0].text
                print(output[:300] + "..." if len(output) > 300 else output)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")

            # Test 5: get_top_contributors
            print("\n[5/5] Testing: get_top_contributors")
            print("-"*60)
            try:
                result = await session.call_tool(
                    "get_top_contributors",
                    arguments={"limit": 3}
                )
                output = result.content[0].text
                print(output)
                print("✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}")

            print("\n" + "="*60)
            print("All Tests Completed!")
            print("="*60)


if __name__ == "__main__":
    asyncio.run(test_all_tools())

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
import asyncio


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["qdrant_mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "search_qdrant",
                {
                    "query": "What is Qdrant?",
                    "collection": "local_docs",
                    "limit": 3
                }
            )

            print("\n✅ MCP Response:")

            for block in result.content:
                print("-", block.text)


asyncio.run(main())
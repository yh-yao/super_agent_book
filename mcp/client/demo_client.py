# client/demo_client.py
import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 用 Python 启动你的 FastMCP 服务器（无缓冲）
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"

    server = StdioServerParameters(
        command=sys.executable,
        args=["-u", "-m", "mcp_demo.server"],  # -u 无缓冲；以模块方式启动
        env=env,
    )

    # 用官方 SDK 的 stdio_client + ClientSession 管理握手与通讯
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            # 1) initialize（SDK 内部会做协议版本协商）
            await session.initialize()

            # 2) 列出工具
            tools_resp = await session.list_tools()
            tool_names = [t.name for t in tools_resp.tools]
            print("tools:", tool_names)

            # 3) 调用 add
            add_resp = await session.call_tool("add", {"a": 1.5, "b": 2.25})
            print("add ->", add_resp.content)

            # 4) 调用 read_file
            rf_resp = await session.call_tool("read_file", {"path": "hello.txt"})
            print("read_file ->", rf_resp.content)

            

if __name__ == "__main__":
    asyncio.run(main())

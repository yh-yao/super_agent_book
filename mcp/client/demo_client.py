# client/demo_client.py
# MCP 演示客户端：通过 STDIO 与 FastMCP 服务器通信
import asyncio
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 用 Python 启动 FastMCP 服务器（无缓冲模式）
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"

    # 获取服务器脚本的绝对路径
    server_script = Path(__file__).parent.parent / "src" / "mcp_demo" / "server.py"
    
    server = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(server_script)],  # -u 无缓冲；直接运行服务器脚本
        env=env,
    )

    # 使用官方 SDK 的 stdio_client + ClientSession 管理握手与通讯
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            # 1) 初始化（SDK 内部会进行协议版本协商）
            await session.initialize()

            # 2) 列出可用工具
            tools_resp = await session.list_tools()
            tool_names = [t.name for t in tools_resp.tools]
            print("可用工具:", tool_names)

            # 3) 调用 add 工具
            add_resp = await session.call_tool("add", {"a": 1.5, "b": 2.25})
            print("add 结果 ->", add_resp.content)

            # 4) 调用 read_file 工具
            rf_resp = await session.call_tool("read_file", {"path": "hello.txt"})
            print("read_file 结果 ->", rf_resp.content)

            

if __name__ == "__main__":
    asyncio.run(main())

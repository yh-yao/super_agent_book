# client/openai_client.py
# MCP + OpenAI 集成示例：使用 OpenAI 的函数调用功能来调用 MCP 工具
import asyncio
import os
import sys
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

async def main():
    """
    演示如何将 MCP 工具与 OpenAI 的函数调用功能集成。
    OpenAI 模型会决定何时调用哪些 MCP 工具来完成用户的请求。
    """
    
    # 初始化 OpenAI 客户端
    # 确保设置了 OPENAI_API_KEY 环境变量
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("=" * 60)
    print("🤖 MCP + OpenAI 集成演示")
    print("=" * 60)
    print()
    
    # 启动 MCP 服务器
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    
    server_script = Path(__file__).parent.parent / "src" / "mcp_demo" / "server.py"
    
    server = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(server_script)],
        env=env,
    )
    
    print("🚀 正在启动 MCP 服务器...")
    
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化 MCP 会话
            await session.initialize()
            print("✅ MCP 服务器已连接\n")
            
            # 获取可用的 MCP 工具
            tools_resp = await session.list_tools()
            print(f"📋 发现 {len(tools_resp.tools)} 个可用工具:")
            for tool in tools_resp.tools:
                print(f"   • {tool.name}: {tool.description}")
            print()
            
            # 将 MCP 工具转换为 OpenAI 函数格式
            openai_tools = []
            for tool in tools_resp.tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                    }
                }
                openai_tools.append(openai_tool)
            
            # 用户查询示例
            user_queries = [
                "请帮我计算 15.5 加 24.3 等于多少？",
                "请读取 hello.txt 文件的内容",
                "请帮我搜索一下 Python MCP 相关的信息"
            ]
            
            for query in user_queries:
                print("=" * 60)
                print(f"💬 用户: {query}")
                print("-" * 60)
                
                # 构建对话消息
                messages = [
                    {
                        "role": "system",
                        "content": "你是一个有用的助手，可以使用工具来帮助用户完成任务。请用中文回答。"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ]
                
                # 调用 OpenAI API
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                
                # 检查是否需要调用工具
                if assistant_message.tool_calls:
                    print(f"🔧 AI 决定调用工具:")
                    
                    # 将助手的响应添加到消息历史
                    messages.append(assistant_message)
                    
                    # 执行工具调用
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        print(f"   → {tool_name}({tool_args})")
                        
                        # 通过 MCP 调用实际的工具
                        try:
                            result = await session.call_tool(tool_name, tool_args)
                            tool_result = str(result.content)
                            print(f"   ✓ 工具返回: {tool_result[:100]}...")
                            
                            # 将工具结果添加到消息历史
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_result
                            })
                        except Exception as e:
                            error_msg = f"工具调用失败: {str(e)}"
                            print(f"   ✗ {error_msg}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg
                            })
                    
                    # 获取最终响应
                    final_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                    )
                    
                    final_message = final_response.choices[0].message.content
                    print(f"\n🤖 AI: {final_message}")
                else:
                    # 直接返回响应（无需工具）
                    print(f"🤖 AI: {assistant_message.content}")
                
                print()
            
            print("=" * 60)
            print("✅ 演示完成！")
            print("=" * 60)

if __name__ == "__main__":
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
        print("   示例: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    asyncio.run(main())

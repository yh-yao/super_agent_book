from __future__ import annotations

import os
import re
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import httpx
from mcp.server.fastmcp import FastMCP

# ---- 配置文件访问的安全基础目录 ----
print("📂 [初始化] 配置文件访问基础目录...", file=sys.stderr)
BASE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"
BASE_DIR.mkdir(parents=True, exist_ok=True)
print(f"   ✓ 基础目录: {BASE_DIR}", file=sys.stderr)

SAMPLE_FILE = BASE_DIR / "hello.txt"
if not SAMPLE_FILE.exists():
    print("   ✓ 创建示例文件 hello.txt", file=sys.stderr)
    SAMPLE_FILE.write_text("你好！这是通过 MCP read_file 工具读取的 sample_data/hello.txt 文件内容。\n", encoding="utf-8")
else:
    print("   ✓ 示例文件 hello.txt 已存在", file=sys.stderr)

print("🚀 [初始化] 创建 FastMCP 服务器实例...", file=sys.stderr)
mcp = FastMCP("mcp-demo")
print("   ✓ 服务器实例创建成功", file=sys.stderr)

# ---------- 工具 ----------

@mcp.tool()
def add(a: float, b: float) -> float:
    """将两个数字相加并返回结果。"""
    print(f"🔢 [工具调用] add(a={a}, b={b})", file=sys.stderr)
    result = a + b
    print(f"   ✓ 计算结果: {result}", file=sys.stderr)
    return result

# 支持使用 SerpAPI 进行真实搜索（支持百度、Google 等）
# 需要设置环境变量: SERPAPI_API_KEY
# 申请地址: https://serpapi.com/
SERPAPI_URL = "https://serpapi.com/search"
ALLOWED_HOSTS = {"serpapi.com"}

# 演示数据：当没有配置 API Key 时使用
DEMO_SEARCH_RESULTS = {
    "python mcp": [
        {
            "title": "Model Context Protocol (MCP) - 官方文档",
            "snippet": "MCP 是一个开放协议，用于在 AI 应用和外部工具/数据源之间实现无缝集成。通过标准化的接口，让 AI 模型可以安全地访问本地和远程资源。",
            "url": "https://modelcontextprotocol.io"
        },
        {
            "title": "Python SDK for MCP - GitHub",
            "snippet": "官方 Python SDK，提供了构建 MCP 服务器和客户端的完整功能。包含 FastMCP 快速开发工具，让你用几行代码就能创建 MCP 服务器。",
            "url": "https://github.com/modelcontextprotocol/python-sdk"
        },
        {
            "title": "MCP 快速入门教程",
            "snippet": "学习如何使用 Python 构建 MCP 服务器，暴露工具和资源给 AI 应用使用。包含完整的代码示例和最佳实践。",
            "url": "https://modelcontextprotocol.io/quickstart"
        }
    ],
    "default": [
        {
            "title": "搜索演示结果",
            "snippet": "这是一个演示结果。要使用真实搜索，请设置 SERPAPI_API_KEY 环境变量。SerpAPI 支持百度、Google、Bing 等多个搜索引擎。",
            "url": "https://serpapi.com"
        }
    ]
}

@mcp.tool()
def search_http(query: str, engine: str = "baidu") -> List[Dict[str, str]]:
    """
    执行网络搜索并返回结果。
    支持多个搜索引擎：baidu（百度）、google（谷歌）、bing（必应）等。
    
    如果设置了 SERPAPI_API_KEY 环境变量，将使用真实的搜索 API。
    否则返回演示结果（用于教学和测试）。
    """
    print(f"🔍 [工具调用] search_http(query='{query}', engine='{engine}')", file=sys.stderr)
    
    # 检查是否配置了 SerpAPI Key
    api_key = os.getenv("SERPAPI_API_KEY")
    
    if api_key:
        # 使用真实的 SerpAPI
        print(f"   → 使用 SerpAPI 进行真实搜索 (引擎: {engine})", file=sys.stderr)
        
        params = {
            "q": query,
            "engine": engine,
            "api_key": api_key,
            "num": 5  # 返回前5个结果
        }
        
        try:
            with httpx.Client(timeout=15.0, headers={"User-Agent": "mcp-demo/0.1"}) as client:
                r = client.get(SERPAPI_URL, params=params)
                r.raise_for_status()
                print(f"   ✓ 请求成功 (状态码: {r.status_code})", file=sys.stderr)
                
                data = r.json()
                results = []
                
                # 解析不同搜索引擎的结果
                if engine == "baidu":
                    # 百度搜索结果
                    for item in data.get("organic_results", [])[:5]:
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                            "url": item.get("link", "")
                        })
                else:
                    # Google/Bing 等其他搜索引擎
                    for item in data.get("organic_results", [])[:5]:
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                            "url": item.get("link", "")
                        })
                
                print(f"   ✓ 解析到 {len(results)} 个搜索结果", file=sys.stderr)
                return results
                
        except Exception as e:
            print(f"   ✗ 搜索失败: {str(e)}", file=sys.stderr)
            print(f"   → 降级到演示模式", file=sys.stderr)
            # 失败时降级到演示结果
            return _get_demo_results(query)
    else:
        # 使用演示结果
        print(f"   → 未配置 SERPAPI_API_KEY，使用演示结果", file=sys.stderr)
        print(f"   ℹ️  提示: 设置 SERPAPI_API_KEY 环境变量以使用真实搜索", file=sys.stderr)
        return _get_demo_results(query)

def _get_demo_results(query: str) -> List[Dict[str, str]]:
    """获取演示搜索结果"""
    normalized_query = query.lower().strip()
    
    # 尝试匹配预设的演示数据
    for key, results in DEMO_SEARCH_RESULTS.items():
        if key != "default" and key in normalized_query:
            print(f"   ✓ 找到匹配的演示结果: '{key}'", file=sys.stderr)
            return results
    
    # 返回默认演示结果
    print(f"   → 返回默认演示结果", file=sys.stderr)
    return DEMO_SEARCH_RESULTS["default"]

def _safe_join(base: Path, relative: str) -> Path:
    print(f"   → 安全路径检查: base={base}, relative={relative}", file=sys.stderr)
    p = (base / relative).resolve()
    if not str(p).startswith(str(base.resolve())):
        print(f"   ✗ 检测到路径遍历攻击", file=sys.stderr)
        raise ValueError("检测到路径遍历攻击")
    print(f"   ✓ 路径安全验证通过: {p}", file=sys.stderr)
    return p

@mcp.tool()
def read_file(path: str) -> str:
    """
    读取沙箱化的 sample_data 目录下的 UTF-8 文本文件。
    示例：path='hello.txt'
    """
    print(f"📄 [工具调用] read_file(path='{path}')", file=sys.stderr)
    p = _safe_join(BASE_DIR, path)
    
    if not p.exists() or not p.is_file():
        print(f"   ✗ 文件未找到: {p}", file=sys.stderr)
        raise FileNotFoundError(f"{p} 未找到")
    
    print(f"   → 读取文件: {p}", file=sys.stderr)
    content = p.read_text(encoding="utf-8")
    print(f"   ✓ 成功读取 {len(content)} 个字符", file=sys.stderr)
    return content


# ---------- 资源 ----------

@mcp.resource("sample://hello.txt")
def sample_text_resource() -> Tuple[str, bytes]:
    """
    服务器暴露的简单资源示例。
    返回：(MIME 类型, 字节数据)
    """
    print(f"📦 [资源访问] sample://hello.txt", file=sys.stderr)
    print(f"   → 读取文件: {SAMPLE_FILE}", file=sys.stderr)
    data = SAMPLE_FILE.read_bytes()
    print(f"   ✓ 成功读取 {len(data)} 字节", file=sys.stderr)
    return "text/plain; charset=utf-8", data


def main() -> None:
    # 通过 stdio 运行服务器
    print("=" * 60, file=sys.stderr)
    print("🎯 [启动] MCP 服务器开始运行", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("📡 等待客户端通过 STDIO 连接...", file=sys.stderr)
    print("", file=sys.stderr)
    mcp.run()

if __name__ == "__main__":
    print("", file=sys.stderr)
    print("🌟 MCP 演示服务器", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    main()

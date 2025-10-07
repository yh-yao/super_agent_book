# MCP 演示项目 (Python)

这是一个**教学级别**的 **Model Context Protocol (MCP)** 实现，使用官方 Python SDK 构建。
它包含：

- 一个 **FastMCP** 服务器，暴露了几个工具和资源
- 一个**小型本地客户端**，通过 STDIO 使用类似 LSP 的 `Content-Length` 帧格式与 MCP 通信
- 不含硬编码的密钥；需要时通过环境变量配置

## 快速开始

```bash
# 1) 安装依赖
pip install -r requirements.txt

# 2) 运行服务器（前台运行）
python src/mcp_demo/server.py
```

在另一个终端（使用相同的虚拟环境），运行演示客户端，它会为你启动服务器并通过 MCP 调用工具：

```bash
python client/demo_client.py
```

你应该会看到：
- 协议 `initialize` 握手
- 工具列表
- 成功调用 `add`、`search_http` 和 `read_file` 工具

### OpenAI 集成示例

运行 OpenAI 集成客户端，演示如何让 AI 智能调用 MCP 工具：

```bash
# 设置 OpenAI API 密钥
export OPENAI_API_KEY='your-api-key-here'

# (可选) 设置 SerpAPI 密钥以启用真实搜索功能（支持百度、Google 等）
export SERPAPI_API_KEY='your-serpapi-key-here'

# 运行 OpenAI 集成示例
python client/openai_client.py
```

这个示例展示了：
- 将 MCP 工具自动转换为 OpenAI 函数格式
- OpenAI 模型智能决定何时调用哪些工具
- 工具调用结果反馈给 AI 生成最终回答
- 完整的对话流程（用户 → AI → 工具 → AI → 用户）

**关于搜索功能：**
- 默认使用演示数据（无需 API Key）
- 设置 `SERPAPI_API_KEY` 后可使用真实搜索（支持百度、Google、Bing 等）
- SerpAPI 申请地址: https://serpapi.com （有免费额度）

## 内容说明

### 服务器

- `src/mcp_demo/server.py` — FastMCP 服务器，暴露：
  - `add(a, b)` — 数字加法工具
  - `search_http(query, engine="baidu")` — 网络搜索工具
    - 支持多个搜索引擎：百度（baidu）、谷歌（google）、必应（bing）等
    - 默认使用演示数据，设置 `SERPAPI_API_KEY` 后使用真实搜索
  - `read_file(path)` — 文件读取工具
    - 读取 `sample_data` 文件夹下的文件（沙箱化）
    - 防止路径遍历攻击
  - 一个示例 **resource**：`sample://hello.txt`

### 客户端

- `client/demo_client.py` — 基础 MCP 客户端：
  - 通过 STDIO 以子进程方式启动服务器
  - 发送带有协议版本的 `initialize` 消息
  - 通过 `tools/list` 列出工具
  - 通过 `tools/call` 调用工具
  - 适合学习 MCP 协议的基本工作流程

- `client/openai_client.py` — OpenAI 集成客户端：
  - 演示如何将 MCP 工具与 OpenAI 的函数调用功能集成
  - 自动将 MCP 工具转换为 OpenAI 函数格式
  - 让 AI 模型智能决定何时调用哪些工具
  - 展示完整的 AI Agent 工作流程

## 说明

- 使用**官方 MCP SDK**（PyPI 上的 `mcp` 包）和 FastMCP 辅助工具。
- 传输方式是 **STDIO + Content-Length** 帧格式（LSP 风格），符合当前 MCP 规范。
- 本项目避免硬编码外部令牌/密钥。HTTP 工具仅使用公共端点。

## 配置说明

### 环境变量

- `OPENAI_API_KEY` - OpenAI API 密钥（运行 `openai_client.py` 时必需）
- `SERPAPI_API_KEY` - SerpAPI 密钥（可选，用于真实搜索功能）
  - 不设置时使用演示数据
  - 设置后支持百度、Google、Bing 等多个搜索引擎
  - 申请地址: https://serpapi.com

## 安全性

- 文件工具被**沙箱化**到 `sample_data/` 目录，拒绝该目录外的路径访问
- 搜索工具使用可信的第三方 API（SerpAPI），避免直接网页爬取
- 所有外部请求都有超时和错误处理机制
- 有关生产级别的安全指南，请参阅 MCP 官方规范和最新的安全文档

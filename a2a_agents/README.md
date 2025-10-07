# Agent 协作（使用 Google A2A SDK）

## 🎯 概述

本项目展示如何使用 **Google 官方 A2A Python SDK** 构建标准化的多 Agent 协作系统。

### 核心特性
- ✅ 标准化的 Agent-to-Agent 通信协议
- ✅ Agent Card 服务发现机制
- ✅ 类型安全的消息传递
- ✅ 支持多种协作模式（串行、并行、条件路由、管道）
- ✅ 生产级代码质量
- 🤖 集成 OpenAI GPT-4o-mini 提供智能能力

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：`a2a-sdk`, `fastapi`, `uvicorn`, `httpx`, `openai`, `python-dotenv`

### 2. 配置 OpenAI API Key

```
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动 Agent 服务

```bash
# 启动 4 个 Agent（需要 4 个终端）
python agents/collector_agent.py    # 端口 8001
python agents/summarizer_agent.py   # 端口 8002
python agents/translator_agent.py   # 端口 8003
python agents/classifier_agent.py   # 端口 8004
```

### 4. 验证服务

访问 Agent Card 端点：
```bash
curl http://localhost:8001/.well-known/agent-card.json
```

### 5. 运行示例

```bash
python clients/01_sequential.py    # 串行协作
python clients/02_parallel.py      # 并行协作
python clients/03_conditional.py   # 条件路由
python clients/04_pipeline.py      # 复杂管道
```

---

## 📚 协作模式

| 模式 | 工作流 | 适用场景 |
|------|--------|---------|
| **串行** | A → B → C | 顺序依赖的任务 |
| **并行** | [A, B, C] → Merge | 独立任务并发 |
| **条件路由** | A → Router → [B/C/D] | 根据条件选择路径 |
| **管道** | Multi-stage Pipeline | 企业级复杂工作流 |

---

## 🏗️ Agent 服务说明

| Agent | 端口 | 功能 | AI 模型 | 输入 | 输出 |
|-------|------|------|---------|------|------|
| **Collector** | 8001 | 收集新闻 | GPT-4o-mini (请求解析) | 主题、数量 | 新闻列表 |
| **Summarizer** | 8002 | 生成摘要 | GPT-4o-mini | 原始文本 | 摘要文本 |
| **Translator** | 8003 | 文本翻译 | GPT-4o-mini | 文本、语言 | 翻译结果 |
| **Classifier** | 8004 | 内容分类 | GPT-4o-mini | 文本 | 分类标签 |

**所有 Agent 均使用 OpenAI GPT-4o-mini 模型提供智能能力。**

---

## 📖 核心 API 示例

### 创建 Agent 服务端

```python
from a2a.server import A2AServer, create_app
from a2a.types import AgentCard, Skill, Message, Part, TextPart, Role

class MyAgent(A2AServer):
    def __init__(self):
        agent_card = AgentCard(
            name="My Agent",
            description="我的智能代理",
            url="http://localhost:8000",
            skills=[Skill(id="my_skill", name="我的技能")]
        )
        super().__init__(agent_card=agent_card)
    
    async def handle_message(self, message: Message) -> Message:
        text = message.parts[0].root.text
        return Message(
            role=Role.AGENT,
            parts=[Part(root=TextPart(text=f"处理: {text}"))]
        )
```

### 调用 Agent 客户端

```python
from a2a.client import ClientFactory, create_text_message_object

client = await ClientFactory.create_client("http://localhost:8000")
message = create_text_message_object("你好")

async for event in client.send_message(message):
    if hasattr(event, 'parts'):
        print(event.parts[0].root.text)
```

---

## 🔍 A2A 核心概念

### 1. Agent Card
Agent 的"名片"，描述能力和接口，位于 `/.well-known/agent-card.json`

### 2. Message Format
标准化消息格式，包含 `role`、`parts`、`message_id` 等字段

### 3. 服务发现
客户端通过 Agent Card 自动发现和验证 Agent 能力

---

## 📁 项目结构

```
a2a/
├── README.md
├── requirements.txt
├── agents/              # Agent 服务（使用 A2AServer）
│   ├── collector_agent.py
│   ├── summarizer_agent.py
│   ├── translator_agent.py
│   └── classifier_agent.py
└── clients/             # 客户端示例（使用 ClientFactory）
    ├── 01_sequential.py
    ├── 02_parallel.py
    ├── 03_conditional.py
    └── 04_pipeline.py
```

# 从零构建AIAgent：大模型驱动的智能体设计与实战

<p align="right">语言：<b>中文</b> | <a href="README_EN.md">English</a></p>

本仓库为《从零构建AIAgent：大模型驱动的智能体设计与实战》的配套代码与范例合集。

- 购买/了解本书（微信小店）：https://store.weixin.qq.com/shop/a/eYQqnHzVRis7l0I

<p align="center">
  <img src="book_cover.png" alt="《从零构建AIAgent》封面" width="420" />
</p>

本仓库收录了可直接运行的多种智能体参考实现，覆盖 A2A 协作、RAG 客服、教育记忆、医疗合规、安全法律、多模态创意、交易决策、MCP 工具协议、编程智能体、自我进化报告与超级智能体编排等典型场景。旨在作为学习与落地的“配方手册”。

> 说明：各子项目彼此独立，进入对应目录后，按该目录下的 README/说明运行。

---

## 一键速览

- Python 版本：3.9+（推荐 3.10/3.11）
- 通用步骤：
  1) 进入子项目目录
  2) 创建虚拟环境并激活（可选）
  3) 安装依赖：`pip install -r requirements.txt`
  4) 配置必要的环境变量（如 `OPENAI_API_KEY` 等）
  5) 按子项目 README 的命令运行

常用环境变量（按需）：
- `OPENAI_API_KEY`：OpenAI 接口密钥
- `PINECONE_API_KEY` / `PINECONE_INDEX`：Pinecone 向量库
- `GOOGLE_API_KEY` / `GOOGLE_CSE_ID`：Google 自定义搜索
- `SERPAPI_API_KEY`：SerpAPI 搜索

---

## 示例目录（与章节主题对应）

- mcp服务端与客户端 — Model Context Protocol 教学实现，含本地 MCP 服务器与两个客户端（基础/集成 OpenAI 函数调用），演示工具发现与调用。
- 智能体技能skills — 使用真实 OpenAI 做推理 + 显式技能声明（SKILL.md），无 MCP 的基线版本。
- a2a_智能体 — 基于 Google A2A SDK 的多智能体协作（串行/并行/条件/管道）；提供 4 个可独立启动的 Agent 与 4 个客户端示例。
- RAG_智能客服与知识问答 — LangChain + Pinecone + FastAPI 的企业客服智能体（FAQ、工单、反馈、记忆）。
- 多模态创意生成 — 文案/设计/校对多 Agent 协作，集成 Diffusers（示例命令行）。
- 编程智能体 — 自主代码库改造智能体（smartcoder 命令，计划→试运行→应用→验证）。
- 个性化与记忆_教育辅导 — 基于记忆与自适应算法（间隔复习/CEFR）的英语学习助手（CLI）。
- 自我演进_商业报告 — 带反思与外部搜索的自进化商业报告代理（多轮评分与改写）。
- 多角色游戏对话体 — 基于 LangGraph 的 NPC 智能对话与路由（村长/铁匠/药师）。
- 实时多智能体_金融决策 — 交易代理教学版（规则/LLM/混合策略，流式输出与报告）。
- 医疗健康智能体 — 合规优先的医疗助手（免责声明/引用/审计/隐私/RAG/CLI+API）。
- 法律智能体 — 法规问答（RAG）、合规差距分析、合同审查（FastAPI+FAISS+OpenAI）。
- 超级智能体实战 — Manus+ 风格的多节点编排（Planner/Researcher/Writer/Reflector），含 RAG/安全检查与轨迹可视化工具。

提示：上列示例分别对应书中关于「多智能体协作」「工具与协议（MCP）」「RAG 检索与工程化」「个性化与记忆」「安全与合规」「多模态协作」「LangGraph 编排」「策略与交易」「基于技能的 Agent」「编程代理自动化」「自我反思与演进」「端到端超级智能体」等章节主题。

---

## 与本书配合使用的建议路径

1) 先通读「智能体基础与架构」章节，了解核心概念（Agent、工具、记忆、RAG、编排、评估）。
2) 选择一个你最关心的应用场景，从对应子目录开始运行与改造。
3) 跟随书中清单完成：配置环境 → 启动服务 → 调试参数 → 评估与迭代。
4) 尝试跨章节组合：例如将「RAG」与「多智能体编排」结合，或在「法律/医疗」场景中引入更严格的安全与审计策略。

---

## 快速开始（示例命令）

以下命令在对应子目录内执行；如需 API Key，请先 `export` 环境变量。

- MCP Demo（mcp服务端与客户端）
  - 服务器：`python src/mcp_demo/server.py`
  - 演示客户端：`python client/demo_client.py`
  - OpenAI 集成：`export OPENAI_API_KEY=... && python client/openai_client.py`

- Agent Skills（智能体技能skills）
  - 运行：`python main.py`

- A2A 多 Agent（a2a_智能体）
  - 启动服务（四终端）：
    - `python agents/collector_agent.py`（:8001）
    - `python agents/summarizer_agent.py`（:8002）
    - `python agents/translator_agent.py`（:8003）
    - `python agents/classifier_agent.py`（:8004）
  - 运行客户端：`python clients/01_sequential.py`（并行/条件/管道同理）

- 客服 RAG（RAG_智能客服与知识问答）
  - 索引构建：`python ingest/index_pinecone.py`
  - 服务：`uvicorn app.main:app --reload --port 8000`

- 多模态创意（多模态创意生成）
  - 示例：`python main.py --product "夏日柠檬饮料" --audience "年轻人"`

- 编程智能体（编程智能体）
  - 安装：`pip install -e .`
  - 运行：`smartcoder auto -p ./examples/demo_project -i "你的指令" [--apply]`

- 英语学习助手（个性化与记忆_教育辅导）
  - CLI 会话：`python main.py`
  - 演示：`python demo.py`

- 自进化报告（自我演进_商业报告）
  - 示例：`python main.py --prompt "分析苹果公司的市场策略" --steps 5`

- 游戏 NPC（多角色游戏对话体）
  - 运行：`python -m game_npc_langgraph.main`

- 交易决策（实时多智能体_金融决策）
  - 规则策略：`python streaming_main.py --mode rule`
  - LLM 策略：`python streaming_main.py --mode llm`
  - 混合策略：`python streaming_main.py --mode hybrid`

- 医疗健康助手（医疗健康智能体）
  - 服务：`uvicorn app.main:app --reload`
  - CLI 示例：`python app/cli.py --question "头痛怎么办"`

- 法律合规助手（法律智能体）
  - 复制环境：`cp .env.example .env` 后 `uvicorn app.main:app --reload`

- 超级智能体（超级智能体实战）
  - 服务：`uvicorn app.main:app --reload`
  - 打开 swagger：`http://127.0.0.1:8000/docs`

---

## 开发与环境建议

- 推荐使用虚拟环境：
  - venv：`python -m venv .venv && source .venv/bin/activate`
  - 或 conda/mamba 等
- 不同子项目的 `requirements.txt` 互不相同；请在各自目录内单独安装。
- 若使用向量库与外部搜索，请准备并配置对应密钥与索引参数。

---

## 常见问题（FAQ）

- 端口占用：修改 `uvicorn` 端口或停止占用进程。
- OpenAI 报错：检查 `OPENAI_API_KEY` 是否生效、网络与模型名是否匹配。
- 向量索引失败：确认维度（如 `text-embedding-3-small` 为 512）与索引参数一致；必要时重建索引。
- Import/依赖冲突：在各子项目独立环境内安装运行，避免全局污染。

---

## 许可证

本仓库遵循根目录的 LICENSE。详情见 LICENSE 文件。

---

## 免责声明

- 所有代码主要用于教学与演示，尤其是医疗与法律类项目，均不构成专业建议或医疗/法律服务。
- 生产使用前请务必进行安全、合规、隐私与可靠性评估，并替换示例数据与策略。

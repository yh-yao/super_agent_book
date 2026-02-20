# Build AI Agents from Scratch: LLM‑Driven Agent Design and Practice

<p align="right">Language: <a href="README.md">中文</a> | <b>English</b></p>

This repository is the companion codebase for the book “Build AI Agents from Scratch: Design and Practice with LLM-driven Agents”.

- Purchase/Info (WeChat Store): https://store.weixin.qq.com/shop/a/eYQqnHzVRis7l0I

<p align="center">
  <img src="book_cover.png" alt="Book Cover: Build AI Agents from Scratch" width="420" />
</p>

It contains runnable reference implementations across typical scenarios: A2A collaboration, RAG helpdesk, education with memory, healthcare safety & compliance, legal compliance, multimodal creativity, trading agents, MCP tools protocol, coding assistant agent, self-evolving business reports, and a Manus+-style orchestrated super-agent.

> Note: Each subproject is standalone. Enter its folder and follow its README to run.

---

## Quick Overview

- Python: 3.9+ (recommend 3.10/3.11)
- Common steps:
  1) cd into a subproject
  2) (Optional) create & activate a virtual env
  3) Install deps: `pip install -r requirements.txt`
  4) Export required env vars (e.g., `OPENAI_API_KEY`)
  5) Follow the subproject README to run

Common environment variables (as needed):
- `OPENAI_API_KEY`
- `PINECONE_API_KEY` / `PINECONE_INDEX`
- `GOOGLE_API_KEY` / `GOOGLE_CSE_ID`
- `SERPAPI_API_KEY`

---

## Examples Catalog (mapped to book topics)

- mcp服务端与客户端 — Model Context Protocol teaching demo with a local MCP server and two clients (basic / OpenAI function-calling integration).
- 智能体技能skills — Real OpenAI reasoning + explicit skills (SKILL.md), no MCP baseline.
- a2a_智能体 — Multi-agent collaboration via Google A2A SDK (sequential/parallel/conditional/pipeline); 4 agents + 4 client demos.
- RAG_智能客服与知识问答 — LangChain + Pinecone + FastAPI helpdesk agent (FAQ, ticket, feedback, memory).
- 多模态创意生成 — Copywriter / Designer (Diffusers) / Proofreader multi-agent workflow.
- 编程智能体 — Autonomous coding agent (smartcoder; plan → dry-run → apply → validate).
- 个性化与记忆_教育辅导 — Memory + adaptive learning (spaced repetition/CEFR) English tutor (CLI).
- 自我演进_商业报告 — Self-evolving business reports with reflection and web search.
- 多角色游戏对话体 — LangGraph NPC dialog and routing (chief/blacksmith/herbalist).
- 实时多智能体_金融决策 — Trading agents (rule/LLM/hybrid) with streaming outputs and reports.
- 医疗健康智能体 — Safety-first healthcare assistant (disclaimer/citations/audit/privacy; RAG; CLI+API).
- 法律智能体 — Legal Q&A (RAG), compliance gap analysis, and contract review (FastAPI+FAISS+OpenAI).
- 超级智能体实战 — Manus+-style orchestrator (Planner/Researcher/Writer/Reflector), mini-RAG, safety, and trace visualization.

---

## Suggested Path with the Book

1) Skim the fundamentals (agent, tools, memory, RAG, orchestration, evaluation).
2) Pick a scenario you care most about and run/modify its subproject.
3) Follow the checklists: environment → run services → tune params → evaluate & iterate.
4) Try cross-topic combos, e.g., combine RAG with orchestration; add stricter safety/audit in healthcare/legal.

---

## Quickstart (sample commands)

Run inside each subfolder; export API keys first if required.

- MCP Demo (mcp服务端与客户端)
  - Server: `python src/mcp_demo/server.py`
  - Demo client: `python client/demo_client.py`
  - OpenAI integration: `export OPENAI_API_KEY=... && python client/openai_client.py`

- Agent Skills（智能体技能skills）
  - `python main.py`

- A2A (a2a_智能体)
  - Agents (4 terminals):
    - `python agents/collector_agent.py` (:8001)
    - `python agents/summarizer_agent.py` (:8002)
    - `python agents/translator_agent.py` (:8003)
    - `python agents/classifier_agent.py` (:8004)
  - Clients: `python clients/01_sequential.py` (others similar)

- Helpdesk RAG (RAG_智能客服与知识问答)
  - Build index: `python ingest/index_pinecone.py`
  - API: `uvicorn app.main:app --reload --port 8000`

- Multimodal Creativity (多模态创意生成)
  - Example: `python main.py --product "Lemon Drink" --audience "Gen Z"`

- Coding Agent (编程智能体)
  - Install: `pip install -e .`
  - Run: `smartcoder auto -p ./examples/demo_project -i "your instruction" [--apply]`

- English Tutor (个性化与记忆_教育辅导)
  - CLI: `python main.py`
  - Demo: `python demo.py`

- Self-evolving Report (自我演进_商业报告)
  - Example: `python main.py --prompt "Analyze Apple’s market strategy" --steps 5`

- Game NPC (多角色游戏对话体)
  - Run: `python -m game_npc_langgraph.main`

- Trading (实时多智能体_金融决策)
  - Rule: `python streaming_main.py --mode rule`
  - LLM: `python streaming_main.py --mode llm`
  - Hybrid: `python streaming_main.py --mode hybrid`

- Healthcare (医疗健康智能体)
  - API: `uvicorn app.main:app --reload`
  - CLI: `python app/cli.py --question "Headache?"`

- Legal (法律智能体)
  - `cp .env.example .env` then `uvicorn app.main:app --reload`

- Super Agent (超级智能体实战)
  - API: `uvicorn app.main:app --reload`
  - Swagger: `http://127.0.0.1:8000/docs`

---

## Dev & Environment Tips

- Use virtual envs (venv/conda). Install deps per subproject to avoid conflicts.
- Prepare keys and index params for vector DBs or external search.

---

## FAQ

- Port in use: change uvicorn port or kill the process.
- OpenAI errors: verify `OPENAI_API_KEY`, network, and model names.
- Vector index fails: ensure dims (e.g., `text-embedding-3-small` = 512) and reset/rebuild if needed.
- Import/deps conflicts: isolate per subproject env.

---

## License

See LICENSE at repo root.

---

## Disclaimer

- Code is for education/demos. Healthcare/legal projects DO NOT constitute professional advice.
- For production, perform security, compliance, privacy, and reliability reviews, and replace sample data/policies.

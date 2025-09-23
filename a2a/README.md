
# A2A（Agent-to-Agent）示例项目

本项目演示两个自治代理（Researcher 与 Writer）在本地知识库上协作，由 Supervisor 负责调度与收尾。无需联网与外部依赖，适合教学与科普演示。

---

## 环境要求
- Python ≥ 3.8
- 支持 macOS / Linux / Windows

> 建议使用虚拟环境：`python -m venv venv && source venv/bin/activate`（Windows 用 `venv\Scripts\activate`）

---

## 快速开始（零安装运行）
在项目根目录执行：
```bash
python -m a2a_demo --task "Explain EOR vs PEO and give 3 practical tips for SMBs" --max-turns 8
```
运行完成后会在 `./output/` 生成：
- `report-YYYYMMDD-HHMMSS.md`：协作产出的 Markdown 报告
- `transcript-YYYYMMDD-HHMMSS.txt`：代理之间的对话转录

---

## 方式二：安装后使用命令行入口
```bash
pip install .
a2a-demo --task "Explain payroll basics in China and HK" --max-turns 8
```

---

## 参数说明
- `--task <str>`：要完成的高阶任务主题（必填）。
- `--max-turns <int>`：回合上限，Supervisor 到达上限或 Writer 产出候选成稿即结束（默认 8）。
- `--data-dir <path>`：本地知识库目录（默认：包内 `data/docs/`）。
- `--output-dir <path>`：输出目录（默认 `./output`）。

示例：
```bash
python -m a2a_demo   --task "Compare EOR and PEO in 3 sections and give tips for SMBs"   --max-turns 8   --data-dir ./data/docs   --output-dir ./output
```

---

## 目录结构
```
a2a_demo/
  agents/
    base.py        # 基类与消息结构
    researcher.py  # 本地检索与片段返回
    writer.py      # 汇总撰写报告并生成引用
    supervisor.py  # 编排轮次、路由消息、判定收尾
  tools/
    file_search.py # 轻量文本检索（.txt）
    rag.py         # 简单打分与片段排序（确定性）
  bus.py           # 内存消息总线
  main.py          # CLI 入口（a2a-demo）
  __main__.py      # 支持 python -m a2a_demo
data/
  docs/            # 示例知识库（纯文本）
tests/
  test_flow.py     # 端到端冒烟测试
```

---

## 工作原理（简述）
1. **Supervisor**：以 `--task` 引导流程，向 Researcher 下达检索请求，跟进 Writer 的追问与成稿状态，控制终止条件（候选成稿或达到 `--max-turns`）。
2. **Researcher**：在 `data/docs` 中检索关键词，返回若干**带行号**的上下文片段（由 `tools.rag` 打分排序）。
3. **Writer**：累计片段，若素材不足则向 Supervisor 触发追问；素材充足后生成结构化 Markdown 报告，并附上**按文件与行号的引用清单**。

整个过程通过 `MessageBus` 以结构化消息传递，保证可追溯与可观测。

---

## 扩展与定制
- **扩充知识库**：向 `data/docs/` 增加 `.txt` 文件即可；也可以用 `--data-dir` 指向自定义目录。
- **新增工具**：在 `a2a_demo/tools/` 下增加模块（例如 CSV 解析、简单计算器），在 Researcher 中组合调用。
- **新增代理**：在 `a2a_demo/agents/` 新建类并在 Supervisor 中编排（如 Reviewer、Critic、Planner 等）。
- **报告模版**：调整 `Writer._compose_report()` 的段落模板与引用格式。

---

## 常见问题（FAQ）
**Q：`python -m a2a_demo` 报错 `No module named a2a_demo.__main__`？**  
A：确认包内存在 `a2a_demo/__main__.py`。本项目已内置。

**Q：没有生成 `report-*.md`？**  
A：可能素材不足或轮次不足。提高 `--max-turns`，或在 `data/docs/` 中加入更多与任务相关的文本。

**Q：如何使用自己的资料？**  
A：将 `.txt` 文件放入新目录并通过 `--data-dir` 指向该目录即可。

**Q：Windows 路径引号问题？**  
A：带空格的路径使用双引号包裹：`--data-dir "C:\my docs\kb"`。

---

## 运行测试
需要安装依赖（仅 `setuptools`/`wheel`）：
```bash
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install .
pytest -q  # 若未安装 pytest，可改为以子进程运行 tests/test_flow.py 的逻辑
```
或直接阅读 `tests/test_flow.py` 中的子进程调用示例。

---

## 许可证
MIT（详见 `LICENSE`）。

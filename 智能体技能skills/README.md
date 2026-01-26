# Agent Skills Demo（No MCP, OpenAI, with SKILL.md）

本示例展示：
- 使用真实 OpenAI LLM 进行推理（生成结构化 IR）
- 使用 Agent Skills 执行确定性能力
- Skill 通过 SKILL.md 声明能力
- Agent 读取 SKILL.md 进行能力感知（不参与内容生成）
- 不使用 MCP，作为教学基线版本

## 运行

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=你的Key
python main.py
```

# 可选: OpenAI API 助手（除非用户设置了OPENAI_API_KEY，否则不使用）。
import os, json, urllib.request, sys

def _print(s: str):
    sys.stdout.write(s + ("\n" if not s.endswith("\n") else ""))
    sys.stdout.flush()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def suggest_plan_with_llm(instruction: str, analysis_summary: str) -> list[dict]:
    if not OPENAI_API_KEY:
        return []
    url = "https://api.openai.com/v1/chat/completions"
    
    system_prompt = """你是一个专业的Python开发者AI智能体。你可以分析代码、建议更改，并提供详细的修改来实现所需功能或修复问题。

请密切注意用户的意图。例如，"来自Alice的问候"与"向Alice问候"是不同的。请仔细分析用户的指令，以理解参与者和操作的方向。
"""
    
    user_prompt = f"""指令:
{instruction}

现有代码分析:
{analysis_summary}

请以以下JSON格式提供计划和实现:
{{
  "plan": ["步骤1", "步骤2", ...],
  "changes": [
    {{
      "file": "path/to/file.py",
      "description": "此更改的作用",
      "code_before": "要替换的精确代码",
      "code_after": "要插入的新代码"
    }}
  ],
  "explanation": "更改的详细说明"
}}

确保code_before与现有代码完全匹配，包括正确的缩进。"""

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {OPENAI_API_KEY}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"]
    try:
        steps = json.loads(text)
        if steps:
            _print(f"LLM生成的计划: {json.dumps(steps, indent=2, ensure_ascii=False)}")
        return steps
    except Exception as e:
        _print(f"解析LLM响应时出错: {text}")
        _print(f"错误: {str(e)}")
        return []

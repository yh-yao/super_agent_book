# Optional: OpenAI API helper (not used unless OPENAI_API_KEY is set by user).
import os, json, urllib.request
import os, json, urllib.request, sys

def _print(s: str):
    sys.stdout.write(s + ("\n" if not s.endswith("\n") else ""))
    sys.stdout.flush()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def suggest_plan_with_llm(instruction: str, analysis_summary: str) -> list[dict]:
    if not OPENAI_API_KEY:
        return []
    url = "https://api.openai.com/v1/chat/completions"
    
    system_prompt = """You are an expert Python developer AI agent. You analyze code, suggest changes, and provide detailed modifications to implement requested features or fix issues.

Pay close attention to the user's intent. A request for a 'greeting from Alice' is different from a 'greeting to Alice'. Analyze the user's instruction carefully to understand the actors and the direction of the action.
"""
    
    user_prompt = f"""Instruction:
{instruction}

Existing Code Analysis:
{analysis_summary}

Provide a plan and implementation in this JSON format:
{{
  "plan": ["step1", "step2", ...],
  "changes": [
    {{
      "file": "path/to/file.py",
      "description": "What this change does",
      "code_before": "exact code to replace",
      "code_after": "new code to insert"
    }}
  ],
  "explanation": "Detailed explanation of the changes"
}}

Ensure code_before matches existing code exactly with correct indentation."""

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
            _print(f"LLM generated plan: {json.dumps(steps, indent=2)}")
        return steps
    except Exception as e:
        _print(f"Error parsing LLM response: {text}")
        _print(f"Error: {str(e)}")
        return []

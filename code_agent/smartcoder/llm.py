# Optional: OpenAI API helper (not used unless OPENAI_API_KEY is set by user).
import os, json, urllib.request

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def suggest_plan_with_llm(instruction: str, analysis_summary: str) -> list[dict]:
    if not OPENAI_API_KEY:
        return []
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You produce explicit, deterministic, safe refactoring plans limited to known actions."},
            {"role": "user", "content": f"Instruction:\n{instruction}\n\nAnalysis:\n{analysis_summary}\n\nReturn a JSON list of steps {{action, args, explain}} using only actions from: add_logging, replace_print, rename_function, fix_mutable_defaults."}
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
        return steps
    except Exception:
        return []

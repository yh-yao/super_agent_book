import re, json, sys
from .llm import suggest_plan_with_llm, OPENAI_API_KEY

SUPPORTED_EDITS = [
# ... existing code ...
    "fix_mutable_defaults",
]

def _print(s: str):
    sys.stdout.write(s + ("\n" if not s.endswith("\n") else ""))
    sys.stdout.flush()

def parse_instruction_to_plan(instruction: str, analysis_summary: str = "") -> list[dict]:
    if OPENAI_API_KEY and analysis_summary:
        _print("(Using LLM to generate plan...)")
        llm_steps = suggest_plan_with_llm(instruction, analysis_summary)
        if llm_steps:
            return llm_steps
    
    _print("(Using local rules to generate plan...)")
    ins = instruction.lower()
    steps: list[dict] = []

    if "logging" in ins or "log" in ins:
        steps.append({"action": "add_logging", "args": {}, "explain": "Add import logging and a function-entry log line to each Python function."})

    if "replace print" in ins or ("print" in ins and "logging" in ins):
        steps.append({"action": "replace_print", "args": {}, "explain": "Replace print(...) calls with logging.info(...)."})

    m = re.search(r"rename (?:function\s+)?([A-Za-z_]\w*)\s+to\s+([A-Za-z_]\w*)", ins)
    if m:
        old, new = m.group(1), m.group(2)
        steps.append({"action": "rename_function", "args": {"old": old, "new": new}, "explain": f"Rename identifier `{old}` to `{new}` within targeted Python files."})

    if "fix mutable" in ins or "mutable default" in ins or "mutable defaults" in ins:
        steps.append({"action": "fix_mutable_defaults", "args": {}, "explain": "Convert list/dict/set defaults to None and initialize inside function."})

    if not steps:
        steps.append({"action": "noop", "args": {}, "explain": "No supported edit was detected. Use flags on `smartcoder edit` to be explicit."})

    return steps

def render_plan_markdown(steps: list[dict]) -> str:
    plan_type = "LLM" if OPENAI_API_KEY else "deterministic"
    lines = [f"# Edit Plan ({plan_type})", ""]
    for i, st in enumerate(steps, 1):
        lines.append(f"### Step {i}: {st['action']}")
        lines.append(f"- Why: {st['explain']}")
# ... existing code ...

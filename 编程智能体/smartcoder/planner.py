import json
from .llm import suggest_plan_with_llm, OPENAI_API_KEY

def parse_instruction_to_plan(instruction: str, analysis_summary: str = "") -> list[dict]:
    """Generate a plan for code modifications."""
    if OPENAI_API_KEY and analysis_summary:
        print("(Using LLM to generate plan...)")
        llm_response = suggest_plan_with_llm(instruction, analysis_summary)
        if llm_response and "changes" in llm_response:
            steps = []
            for change in llm_response["changes"]:
                steps.append({
                    "action": "edit",
                    "args": {
                        "file": change["file"],
                        "old": change["code_before"],
                        "new": change["code_after"]
                    },
                    "explain": change["description"]
                })
            return steps
    
    print("(Using basic analysis to generate plan...)")
    # Simple fallback when LLM is not available
    return [{"action": "noop", "args": {}, "explain": "This operation requires LLM to understand and generate code changes."}]

def render_plan_markdown(steps: list[dict]) -> str:
    plan_type = "LLM" if OPENAI_API_KEY else "deterministic"
    lines = [f"# Edit Plan ({plan_type})", ""]
    if not steps:
        lines.append("No steps were generated for this instruction.")
    else:
        for i, st in enumerate(steps, 1):
            lines.append(f"### Step {i}: {st['action']}")
            lines.append(f"- Why: {st['explain']}")
            if st.get("args"):
                lines.append(f"- Args: `{json.dumps(st['args'])}`")
            lines.append("")
    return "\n".join(lines)

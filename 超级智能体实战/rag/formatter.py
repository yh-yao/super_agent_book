
from typing import List
from app.schemas import Evidence

def format_evidence_block(evidences: List[Evidence]) -> str:
    if not evidences: return ""
    lines = ["", "参考依据："]
    for i, e in enumerate(evidences, 1):
        snip = e.text.strip().replace("\n"," ")[:120]
        lines.append(f"- [{i}] {e.source} · 片段：{snip} ...")
    return "\n".join(lines)

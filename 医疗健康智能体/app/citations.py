from typing import List, Dict, Any
from .models import Evidence

def render_citation_markers(evidences: List[Evidence]) -> str:
    # Build '[1][2]' trail for the bottom of the message if needed
    if not evidences:
        return ""
    tail = " 参考来源: " + " ".join(f"[{i+1}]" for i, _ in enumerate(evidences))
    return tail

def pack_citations(evidences: List[Evidence]) -> List[Dict[str, Any]]:
    return [e.model_dump() for e in evidences]

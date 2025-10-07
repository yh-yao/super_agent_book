import os, glob, yaml
from typing import List, Dict

POLICY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "policies")

def load_policies(names: List[str]) -> List[dict]:
    specs = []
    for n in names:
        fp = os.path.join(POLICY_DIR, f"{n}.yaml")
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                specs.append(yaml.safe_load(f))
    return specs

def evaluate_gaps(fact: dict, policies: List[dict]) -> List[dict]:
    # Extremely simplified rules for demo purposes
    gaps = []
    for p in policies:
        for c in p.get("controls", []):
            status = "partial"
            risk = "medium"
            req = c.get("requirement","")

            # naive heuristics
            if "Records of Processing Activities" in req:
                # Check if the org has any inventory in provided facts (toy rule)
                has_map = "processes" in fact and len(fact["processes"]) > 0
                status = "met" if has_map else "missing"
                risk = "low" if has_map else "high"
            if "breach" in req.lower():
                status = "missing"
                risk = "high"

            gaps.append({
                "control_id": c.get("id",""),
                "status": status,
                "risk": risk,
                "evidence": c.get("evidence",[]),
                "references": c.get("references",[])
            })
    return gaps

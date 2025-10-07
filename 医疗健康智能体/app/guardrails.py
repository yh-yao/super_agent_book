import re
from typing import List, Tuple

RED_FLAG_PATTERNS = [
    r"胸痛.*(冷汗|出汗|呼吸困难)",
    r"中风|偏瘫|口眼歪斜|言语不清",
    r"大出血|喷射呕吐|抽搐",
    r"呼吸困难|窒息",
]

DIAGNOSIS_CLAIMS = [
    r"我诊断为", r"你患有", r"确诊是", r"我给你开药", r"处方如下"
]

def triage_and_block(text: str) -> Tuple[str, bool, List[str]]:
    reasons: List[str] = []
    triage = "green"
    blocked = False

    # Emergency red flags
    if any(re.search(pat, text) for pat in RED_FLAG_PATTERNS):
        triage = "red"
        reasons.append("Detected potential emergency red flags")

    # Hard block on diagnosis/prescription claims
    if any(re.search(pat, text) for pat in DIAGNOSIS_CLAIMS):
        blocked = True
        reasons.append("Potential diagnosis or prescription claim")

    return triage, blocked, reasons

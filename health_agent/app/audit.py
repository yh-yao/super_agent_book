import json, time, orjson, os
from .config import AUDIT_LOG
from .privacy import hash_user

def write_audit(user_id: str, question: str, policy: dict, citations: list):
    rec = {
        "ts": time.time(),
        "user": hash_user(user_id),
        "q": question,
        "policy": policy,
        "citations": citations,
    }
    line = orjson.dumps(rec).decode("utf-8")
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

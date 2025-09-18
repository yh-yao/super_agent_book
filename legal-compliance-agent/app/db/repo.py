import time, hashlib, json, os

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports", "audit_log.jsonl")

def log_event(action: str, payload: dict):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    payload = dict(payload)
    payload["action"] = action
    payload["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

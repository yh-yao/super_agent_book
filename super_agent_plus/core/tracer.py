
import json, os, datetime

class OrchestratorTracer:
    def __init__(self, log_dir="runs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(log_dir, f"trace_{ts}.json")
        self.events = []

    def log(self, node_name, state_before, state_after):
        self.events.append({
            "node": node_name,
            "messages_in": [m for m in state_before.messages],
            "outcome_before": state_before.outcome,
            "outcome_after": state_after.outcome,
            "safety_flags": state_after.safety_flags,
            "citations": [e.source for e in state_after.evidences],
        })

    def save(self):
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(self.events,f,ensure_ascii=False,indent=2)
        return self.path

import json
from pathlib import Path

class RecordAgent:
    def __init__(self, path="outputs/record.json"):
        self.path = Path(path)

    def run(self, student_id, score, feedback):
        record = {"student_id": student_id, "score": score, "feedback": feedback}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            data = []
        data.append(record)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        return record

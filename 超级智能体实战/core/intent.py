
from typing import Dict

class IntentDetector:
    def predict(self, user_input: str, has_image=False, has_audio=False) -> Dict:
        text = user_input.lower()
        intent = "QA"
        if any(k in text for k in ["写", "write", "email", "report", "论文", "draft"]):
            intent = "Write"
        elif any(k in text for k in ["代码", "code", "函数", "脚本"]):
            intent = "Code"
        elif any(k in text for k in ["分析", "chart", "表格", "plot"]):
            intent = "Analyze"
        return {
            "type": intent,
            "slots": {},
            "confidence": 0.85,
            "multimodal": {"has_image": has_image, "has_audio": has_audio},
        }

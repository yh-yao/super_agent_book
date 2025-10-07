
from app.schemas import OrchestratorState

class Analyst:
    def run(self, state: OrchestratorState, summary: str = "") -> OrchestratorState:
        # For demo, just echo a structured analysis placeholder.
        prev = state.scratch.get("analysis","")
        state.scratch["analysis"] = (prev + "\n" if prev else "") + (summary or "分析完成：已生成基础统计与要点。")
        return state

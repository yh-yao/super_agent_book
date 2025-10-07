
from app.schemas import OrchestratorState

class Reflector:
    def _score(self, text: str, evidences):
        if not text:
            return {"task": 0.0}
        base = 0.6
        if evidences:
            base += 0.25
        if len(text) > 40:
            base += 0.05
        return {"task": min(base, 0.95)}

    def evaluate_and_maybe_retry(self, state: OrchestratorState, max_retry: int = 1):
        score = self._score(state.outcome, state.evidences)
        if score["task"] < 0.7 and max_retry > 0:
            tips = "（已根据检索证据进行修正与补充。）"
            state.outcome = (state.outcome or "") + tips
        return state

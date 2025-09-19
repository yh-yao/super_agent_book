
from app.schemas import OrchestratorState

class Planner:
    def __init__(self, router, safety):
        self.router = router
        self.safety = safety

    def plan(self, state: OrchestratorState) -> OrchestratorState:
        intent = state.intent["type"]
        if intent in ("QA", "Write"):
            state.plan = [
                {"agent":"researcher", "params":{"query": state.messages[-1]["content"]}, "reflect": False},
                {"agent":"writer", "params":{}, "reflect": True},
            ]
        elif intent == "Analyze":
            state.plan = [
                {"agent":"researcher", "params":{"query": state.messages[-1]["content"]}, "reflect": False},
                {"agent":"analyst", "params":{"summary":"已从数据与证据中提取关键统计。"}, "reflect": False},
                {"agent":"writer", "params":{}, "reflect": True},
            ]
        else:
            state.plan = [{"agent":"writer", "params":{}, "reflect": True}]
        return state

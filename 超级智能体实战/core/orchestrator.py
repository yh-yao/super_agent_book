
from app.schemas import OrchestratorState
from typing import Dict

class Orchestrator:
    def __init__(self, agents: Dict[str, object], safety, reflector):
        self.agents = agents
        self.safety = safety
        self.reflector = reflector

    def run(self, state: OrchestratorState) -> OrchestratorState:
        for m in state.messages:
            state.safety_flags.extend(self.safety.pre_check(m["content"], state.user))

        state = self.agents["planner"].plan(state)

        for step in state.plan:
            agent = self.agents[step["agent"]]
            state = agent.run(state, **step.get("params", {}))
            if step.get("reflect", False):
                state = self.reflector.evaluate_and_maybe_retry(state)

        state.outcome = self.safety.post_guard(state.outcome or "")
        return state

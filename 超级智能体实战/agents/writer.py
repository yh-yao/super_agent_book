
from app.schemas import OrchestratorState
from rag.formatter import format_evidence_block
from models.llm_clients import get_llm

class Writer:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state: OrchestratorState, **kwargs) -> OrchestratorState:
        user_msg = state.messages[-1]["content"] if state.messages else ""
        ev_block = format_evidence_block(state.evidences)
        analysis = state.scratch.get("analysis","")
        if analysis:
            analysis = "\n\n[分析要点]\n" + analysis
        prompt = "你是一个多代理编排系统的写手代理。\n" + \
                 "用户需求：" + user_msg + analysis + "\n\n" + \
                 "请基于可用的检索证据撰写一段清晰、可执行的回答，并在末尾保留“参考依据”列表：" + \
                 ev_block + "\n"
        draft = self.llm.chat(prompt)
        state.outcome = draft
        return state


from app.schemas import OrchestratorState
from rag.retriever import Retriever

class Researcher:
    def __init__(self, retriever: Retriever = None):
        self.retriever = retriever

    def attach_retriever(self, retriever: Retriever):
        self.retriever = retriever

    def run(self, state: OrchestratorState, query: str = "") -> OrchestratorState:
        if self.retriever:
            evs = self.retriever.query(query or (state.messages[-1]["content"] if state.messages else ""), k=4)
            state.evidences = evs
        return state

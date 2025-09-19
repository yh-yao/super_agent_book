
from typing import List
from app.schemas import Evidence

class Retriever:
    def __init__(self, vs):
        self.vs = vs

    def query(self, q: str, k: int = 4) -> List[Evidence]:
        hits = self.vs.search(q, top_k=k)
        return [Evidence(text=h["text"], source=h["source"], score=h["score"]) for h in hits]

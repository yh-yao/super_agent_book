from typing import Optional, Dict, Any, List, Tuple
from .base import Agent, Message
from ..tools.file_search import LocalFileSearch
from ..tools.rag import rank_snippets

class ResearcherAgent(Agent):
    name = "Researcher"

    def __init__(self, bus, data_dir: str, top_k: int = 6):
        super().__init__(bus)
        self.search = LocalFileSearch(data_dir=data_dir)
        self.top_k = top_k

    def receive(self, message: Message) -> Optional[Message]:
        # Only act on Supervisor or Writer prompts directed to Researcher
        if message.meta.get("target") not in (None, self.name):
            return None

        intent = message.meta.get("intent", "search")
        if intent == "search":
            query = message.content.strip()
            hits = self.search.search(query)
            ranked = rank_snippets(query, hits, top_k=self.top_k)
            payload = {
                "query": query,
                "snippets": ranked,
            }
            return Message(role=self.name, content="SEARCH_RESULTS", meta=payload)
        elif intent == "answer_question":
            # Use the same search to gather context and provide an extractive answer
            query = message.content.strip()
            hits = self.search.search(query)
            ranked = rank_snippets(query, hits, top_k=max(3, self.top_k//2))
            # Construct a short factual answer from top snippet(s)
            answer_lines: List[str] = []
            for snip in ranked[:3]:
                answer_lines.append(snip["text"])
            answer = " ".join(answer_lines)[:1000]
            return Message(role=self.name, content=answer, meta={"query": query, "snippets": ranked})
        else:
            return Message(role=self.name, content=f"Unknown intent: {intent}")

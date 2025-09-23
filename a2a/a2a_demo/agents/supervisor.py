from typing import Optional, Dict, Any
from .base import Agent, Message

class Supervisor(Agent):
    name = "Supervisor"

    def __init__(self, bus, task: str, max_turns: int = 8):
        super().__init__(bus)
        self.task = task.strip()
        self.turns = 0
        self.max_turns = max_turns
        self.finished = False

    def bootstrap(self):
        # Kick off with a search request to Researcher
        return Message(
            role=self.name,
            content=self.task,
            meta={"intent": "search", "target": "Researcher"}
        )

    def receive(self, message: Message) -> Optional[Message]:
        # Route follow-ups and decide when to stop
        if self.finished:
            return None

        self.turns += 1
        if self.turns >= self.max_turns:
            self.finished = True
            return Message(role=self.name, content="MAX_TURNS_REACHED", meta={"intent": "stop"})

        if message.role == "Writer" and message.meta.get("intent") == "draft" and message.meta.get("is_final_candidate"):
            self.finished = True
            # Send system stop signal
            return Message(role=self.name, content="FINAL_DRAFT_READY", meta={"intent": "stop"})
        elif message.role == "Writer" and message.meta.get("intent") == "followup_question":
            q = f"{self.task}. {message.content}"
            return Message(role=self.name, content=q, meta={"intent": "search", "target": "Researcher"})
        else:
            # Default: continue encouraging search breadth
            return Message(role=self.name, content=self.task + " (broaden context)",
                           meta={"intent": "search", "target": "Researcher"})

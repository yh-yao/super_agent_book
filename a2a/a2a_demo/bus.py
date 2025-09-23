from typing import List
from .agents.base import Message

class MessageBus:
    def __init__(self):
        self.log: List[Message] = []

    def publish(self, msg: Message):
        self.log.append(msg)

    def transcript(self) -> List[Message]:
        return list(self.log)

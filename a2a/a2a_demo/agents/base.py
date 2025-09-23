from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class Message:
    role: str  # "user", "system", or agent name
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())

class Agent:
    name: str = "Agent"

    def __init__(self, bus, **kwargs):
        self.bus = bus
        self.state: Dict[str, Any] = {}
        self.config = kwargs

    def receive(self, message: Message) -> Optional[Message]:
        """Process a message and optionally return a reply Message."""
        raise NotImplementedError

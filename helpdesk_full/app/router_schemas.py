from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    query: str

class ChatResponse(BaseModel):
    intent: str
    answer: Optional[str] = None
    ticket_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class FeedbackRequest(BaseModel):
    session_id: str
    score: int
    comment: Optional[str] = None

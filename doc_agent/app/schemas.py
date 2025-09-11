from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str


from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserProfile(BaseModel):
    user_id: str = "u1"
    name: Optional[str] = "Guest"
    domain_prefs: List[str] = []
    style: Dict[str, Any] = {}
    safety_tier: str = "normal"
    roles: List[str] = []

class Intent(BaseModel):
    type: str = "QA"
    slots: Dict[str, Any] = {}
    confidence: float = 0.8
    multimodal: Dict[str, bool] = {}

class Evidence(BaseModel):
    text: str
    source: str
    score: float = 1.0

class OrchestratorState(BaseModel):
    user: UserProfile
    intent: Dict[str, Any]
    messages: List[Dict[str, Any]] = []
    evidences: List[Evidence] = []
    plan: List[Dict[str, Any]] = []
    scratch: Dict[str, Any] = {}
    safety_flags: List[str] = []
    outcome: Optional[str] = None

class ChatRequest(BaseModel):
    user: UserProfile
    message: str

class ChatResponse(BaseModel):
    reply: str
    citations: List[str] = []

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PatientProfile(BaseModel):
    age: Optional[int] = Field(default=None, description="年龄")
    sex: Optional[str] = Field(default=None, description="性别: male/female/other")
    conditions: Optional[List[str]] = Field(default_factory=list, description="已知疾病")
    meds: Optional[List[str]] = Field(default_factory=list, description="用药")
    allergies: Optional[List[str]] = Field(default_factory=list, description="过敏史")

class AskRequest(BaseModel):
    user_id: str
    question: str
    patient: Optional[PatientProfile] = None

class Evidence(BaseModel):
    doc_id: str
    title: str
    chunk: str
    score: float
    source: str

class PolicyDecision(BaseModel):
    triage_level: str   # green / yellow / red
    blocked: bool
    reasons: List[str]

class AskResponse(BaseModel):
    answer: str
    disclaimer: str
    citations: List[Evidence]
    policy: PolicyDecision
    meta: Dict[str, Any] = {}

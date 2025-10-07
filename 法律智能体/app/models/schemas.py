from pydantic import BaseModel, Field
from typing import List, Optional, Any

class QARequest(BaseModel):
    question: str
    jurisdictions: Optional[List[str]] = None
    as_of: Optional[str] = None

class Citation(BaseModel):
    title: str
    url: Optional[str] = None
    date: Optional[str] = None
    snippet: Optional[str] = None

class QAResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    assumptions: List[str] = []
    confidence: float = 0.5
    disclaimer: str

class ComplianceGapRequest(BaseModel):
    fact: dict
    policies: List[str] = Field(default_factory=list)  # e.g., ["gdpr","ccpa"]

class ControlGap(BaseModel):
    control_id: str
    status: str  # "met" | "partial" | "missing"
    risk: str    # "low" | "medium" | "high"
    evidence: List[str] = []
    references: List[dict] = []

class ComplianceGapResponse(BaseModel):
    gaps: List[ControlGap]
    summary: dict

class ContractReviewResponse(BaseModel):
    extracted: dict
    diff_against: str
    risks: List[dict]
    report_url: Optional[str] = None

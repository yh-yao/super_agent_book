from fastapi import APIRouter
from ..models.schemas import ComplianceGapRequest, ComplianceGapResponse, ControlGap
from ..services.rules_engine import load_policies, evaluate_gaps
from ..middleware.guardrails import add_disclaimer

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

@router.post("/gap", response_model=ComplianceGapResponse)
def gap(req: ComplianceGapRequest):
    policies = load_policies(req.policies or ["gdpr","ccpa"])
    gaps = evaluate_gaps(req.fact, policies)
    # naive summary
    high = sum(1 for g in gaps if g["risk"] == "high")
    med = sum(1 for g in gaps if g["risk"] == "medium")
    low = sum(1 for g in gaps if g["risk"] == "low")
    return {
        "gaps": [ControlGap(**g).model_dump() for g in gaps],
        "summary": {
            "high": high, "medium": med, "low": low,
            "disclaimer": add_disclaimer("")
        }
    }

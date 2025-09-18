from fastapi import APIRouter
from ..models.schemas import QARequest, QAResponse, Citation
from ..services import rag, llm
from ..middleware.guardrails import add_disclaimer
import json

router = APIRouter(prefix="/api/qa", tags=["qa"])

QA_SYSTEM_PROMPT = (
    "You are a legal-compliance assistant. You MUST cite sources from provided contexts. "
    "Do not provide legal advice; provide information with jurisdictions and effective dates. "
    "Answer in JSON with fields: answer, citations[], assumptions[], confidence (0-1), disclaimer."
)

def build_user_prompt(question: str, hits):
    # include top passages with metadata
    ctxs = []
    for h in hits:
        ctxs.append({
            "title": h["title"],
            "date": h.get("date"),
            "url": h.get("url"),
            "text": h["text"]
        })
    prompt = {
        "question": question,
        "contexts": ctxs,
        "instructions": [
            "Use only the contexts for factual claims.",
            "List citations with title/url/date and include short supporting snippets.",
            "If insufficient evidence, say so and suggest next steps."
        ]
    }
    return json.dumps(prompt, ensure_ascii=False)

@router.post("", response_model=QAResponse)
def qa(req: QARequest):
    hits = rag.search(req.question, k=6)
    user_prompt = build_user_prompt(req.question, hits)
    raw = llm.chat_json(QA_SYSTEM_PROMPT, user_prompt, max_tokens=800, temperature=0.2)
    data = json.loads(raw)

    # Guarantee disclaimer
    data["disclaimer"] = add_disclaimer(data.get("answer",""))
    # Coerce citations schema
    cites = []
    for c in data.get("citations", []):
        cites.append(Citation(
            title=c.get("title",""),
            url=c.get("url"),
            date=c.get("date"),
            snippet=c.get("snippet")
        ).model_dump())
    data["citations"] = cites
    data.setdefault("assumptions", [])
    data.setdefault("confidence", 0.5)
    return data

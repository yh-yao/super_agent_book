from fastapi import APIRouter
from ..models.schemas import QARequest, QAResponse, Citation
from ..services import rag, llm
from ..middleware.guardrails import add_disclaimer
import json

router = APIRouter(prefix="/api/qa", tags=["qa"])

QA_SYSTEM_PROMPT = (
    "您是一个法律合规助手。您必须引用提供的上下文中的来源。"
    "不要提供法律建议；请提供包含管辖区域和生效日期的信息。"
    "以JSON格式回答，包含字段：answer（答案）、citations[]（引用）、assumptions[]（假设）、confidence（置信度，0-1）、disclaimer（免责声明）。"
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
            "仅使用上下文中的信息进行事实声明。",
            "列出包含标题/链接/日期的引用，并包含简短的支撑片段。",
            "如果证据不足，请说明并建议下一步措施。"
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

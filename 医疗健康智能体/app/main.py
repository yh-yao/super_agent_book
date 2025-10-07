from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .models import AskRequest, AskResponse
from .config import DISCLAIMER
from .privacy import scrub_phi
from .guardrails import triage_and_block
from .rag import RAGIndex
from .prompts import SYSTEM_PROMPT, REFUSAL_PROMPT
from .llm import complete_with_citations
from .citations import render_citation_markers, pack_citations
from .audit import write_audit

app = FastAPI(title="Health Agent (Compliance‑First)")
rag = RAGIndex()

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    # 1) privacy scrub
    q_clean, phi_flag = scrub_phi(payload.question)

    # 2) guardrails: triage + hard blocks
    triage, blocked, reasons = triage_and_block(q_clean)

    # 3) RAG
    evidences = rag.search(q_clean, k=5)
    evidence_tail = render_citation_markers(evidences)

    # 4) LLM synthesis or refusal
    if blocked:
        answer = REFUSAL_PROMPT + "\n" + evidence_tail
    else:
        # Build user prompt with light structure + evidence
        context = "\n\n".join([f"[{i+1}] {e.chunk}" for i, e in enumerate(evidences)])
        user_prompt = (
            f"用户问题: {q_clean}\n"
            f"患者信息(若有): {payload.patient.model_dump() if payload.patient else '{}'}\n"
            f"可用证据: \n{context}\n"
            f"请在'教育信息'范围内回答，提供简单分诊建议，并明确不构成诊断。"
        )
        answer = complete_with_citations(SYSTEM_PROMPT, user_prompt) + "\n" + evidence_tail

    policy = {"triage_level": triage, "blocked": blocked, "reasons": reasons}
    citations = pack_citations(evidences)

    # 5) audit
    write_audit(payload.user_id, payload.question, policy, citations)

    return JSONResponse(AskResponse(
        answer=answer,
        disclaimer=DISCLAIMER,
        citations=evidences,
        policy=policy,
        meta={"phi_scrubbed": phi_flag}
    ).model_dump())

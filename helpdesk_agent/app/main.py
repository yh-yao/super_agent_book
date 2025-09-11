from fastapi import FastAPI
from app.router_schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.chains import build_router
from app.tools import create_or_update_ticket
from app.memory import append_turn, get_history
from app.config import INDEX_NAME

app = FastAPI(title="Helpdesk AI")
router = build_router(INDEX_NAME)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    append_turn(req.session_id, "user", req.query, {"user_id": req.user_id})
    routed = router.invoke({"query": req.query})

    if "create_or_update_ticket" in routed.get("actions", []):
        issue = routed["slots"].get("issue") or req.query
        priority = routed["slots"].get("priority","normal")
        tk = create_or_update_ticket(req.user_id, issue, priority, extra={"history": get_history(req.session_id)})
        msg = f"已为你创建工单 {tk['ticket_id']}（状态：{tk['status']}），我们会尽快处理。"
        append_turn(req.session_id, "assistant", msg, {"intent": routed["intent"], "ticket_id": tk["ticket_id"]})
        return ChatResponse(intent=routed["intent"], answer=msg, ticket_id=tk["ticket_id"])
    else:
        answer = routed.get("answer") or "抱歉，我未能理解，请补充信息。"
        append_turn(req.session_id, "assistant", answer, {"intent": routed["intent"]})
        return ChatResponse(intent=routed["intent"], answer=answer)

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    append_turn(req.session_id, "feedback", f"score={req.score}, comment={req.comment}")
    return {"ok": True}

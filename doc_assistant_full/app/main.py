from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.chains import build_doc_qa
from app.memory import append_turn, get_history

app = FastAPI(title="Doc Assistant")
qa_chain = build_doc_qa("vector_index")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    append_turn(req.session_id, "user", req.query)
    history = get_history(req.session_id)
    answer = qa_chain.invoke({"query": req.query, "history": history})
    append_turn(req.session_id, "assistant", answer)
    return ChatResponse(answer=answer)

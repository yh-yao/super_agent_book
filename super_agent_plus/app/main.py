
from fastapi import FastAPI, UploadFile, File, Form
from app.schemas import ChatRequest, ChatResponse, OrchestratorState
from app.deps import intentor, graph, vs
from tools.file_tools import save_upload, csv_basic_stats
from tools.code_exec import safe_eval

app = FastAPI(title="Manus+ Full (LangGraph + OpenAI)")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    intent = intentor.predict(req.message)
    state = OrchestratorState(
        user=req.user,
        intent=intent,
        messages=[{"role":"user","content": req.message}],
    )
    final_state = graph.invoke(state)
    trace_file = graph.save_trace()  # 保存执行轨迹
    return ChatResponse(
        reply=final_state.outcome or "",
        citations=[e.source for e in final_state.evidences]
    )

@app.post("/ingest/text")
async def ingest_text(text: str = Form(...), source: str = Form("user_note.txt")):
    vs.add_doc(doc_id=source, text=text, source=f"user/{source}")
    return {"ok": True, "indexed": source, "len": len(text)}

@app.post("/ingest/image")
async def ingest_image(file: UploadFile = File(...)):
    data = await file.read()
    path = save_upload("uploads", file.filename, data)
    faux_text = f"Image uploaded: {file.filename}. (OCR placeholder for demo)"
    vs.add_doc(doc_id=file.filename, text=faux_text, source=f"image/{file.filename}")
    return {"filename": file.filename, "bytes": len(data), "indexed_as": "OCR placeholder"}

@app.post("/ingest/audio")
async def ingest_audio(file: UploadFile = File(...)):
    data = await file.read()
    path = save_upload("uploads", file.filename, data)
    faux_text = f"Audio uploaded: {file.filename}. Transcript (demo ASR)."
    vs.add_doc(doc_id=file.filename, text=faux_text, source=f"audio/{file.filename}")
    return {"filename": file.filename, "bytes": len(data), "indexed_as": "ASR placeholder"}

@app.post("/analyze/csv")
async def analyze_csv(file: UploadFile = File(...)):
    data = await file.read()
    path = save_upload("uploads", file.filename, data)
    stats = csv_basic_stats(path)
    summary_lines = [f"{k}: mean={v['mean']:.4f}, stdev={v['stdev']:.4f}, min={v['min']:.4f}, max={v['max']:.4f}" for k,v in stats.items()]
    summary_text = "CSV Summary for " + file.filename + " ::\n" + "\n".join(summary_lines)
    vs.add_doc(doc_id=file.filename + ".summary", text=summary_text, source=f"csv/{file.filename}")
    return {"file": file.filename, "stats": stats}

@app.post("/tool/exec")
async def tool_exec(expr: str = Form(...)):
    value = safe_eval(expr)
    return {"expr": expr, "value": value}

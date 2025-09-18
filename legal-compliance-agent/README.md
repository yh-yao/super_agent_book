# Legal-Compliance Copilot (MVP)

A runnable **Legal-Compliance Copilot** for regulatory Q&A (RAG), basic compliance gap checks, and a lightweight contract review demo.
Built with **FastAPI**, **FAISS**, and **OpenAI** (chat + embeddings).

> ⚠️ This tool does **not** provide legal advice. It is an assistive system that must be reviewed by qualified counsel.

## Features (MVP)
- RAG Q&A over sample GDPR/CCPA texts with **citations** and **timestamps**
- Compliance gap analysis over a tiny demo policy set (YAML → controls)
- Contract review demo: extract a few key clauses and compare against a baseline
- Audit log with prompt/response hashes and timestamps

## Quickstart

1) **Python env**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) **Set environment variables**
Create `.env` from the example and fill your keys:
```bash
cp .env.example .env
# edit .env
```

3) **Run the API**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4) **Try it**
- Q&A:
```bash
curl -X POST http://127.0.0.1:8000/api/qa -H "Content-Type: application/json"   -d '{"question":"What does GDPR say about records of processing?", "jurisdictions":["EU"], "as_of":"2025-09-01"}'
```
- Compliance gap:
```bash
curl -X POST http://127.0.0.1:8000/api/compliance/gap -H "Content-Type: application/json"   -d @examples/fact.json
```

- Contract review:
```bash
curl -F "file=@examples/sample_contract.txt" http://127.0.0.1:8000/api/contracts/review
```

## Notes
- On first run, the app will **build a FAISS index** from the sample corpus in `ingest/corpus/`
- You can add your own regulation texts as `.txt` or `.md` files; restart the server to re-index (or delete `vectorstore/*`)
- Replace the sample YAML in `policies/` with your org’s mapped controls
- All outputs include a disclaimer and are intended for **human review**

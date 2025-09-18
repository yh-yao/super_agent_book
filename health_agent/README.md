# Health Agent (Compliance‑First RAG + LLM)

A reference **medical health assistant** focused on **compliance, safety, and explainability**.
It provides retrieval‑augmented responses with **disclaimers, citations, and audit logs**.
> ⚠️ Educational demo only. Not a medical device. Not a substitute for professional care.

## Features
- **RAG** over trusted local guidelines (e.g., sample clinical guideline snippets in `data/`)
- **LLM** synthesis with explicit **disclaimer + scope control**
- **Guardrails**: triage red‑flags, restricted claims, PHI de‑identification (basic), role‑based prompts
- **Citations**: JSON evidence bundle returned to caller
- **Audit log**: JSONL log with hashed user id + policy decisions
- **FastAPI** server + simple CLI

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn app.main:app --reload
# or run CLI
python app/cli.py --question "持续胸痛并伴随出冷汗，该怎么办？"
```

## Environment
Create `.env` from `.env.example`:
- `OPENAI_API_KEY=`
- `MODEL_NAME=gpt-4o-mini`

## Important Notes
- This code includes **safety blocks** to **refuse diagnosis** and suggest **seek-care pathways** when red‑flags appear.
- You must replace `data/` with your institution’s vetted, licensed guidelines.
- Add your own DPO/IRB/compliance reviews before deployment.

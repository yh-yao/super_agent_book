import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import qa, compliance, contracts

app = FastAPI(title="Legal-Compliance Copilot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qa.router)
app.include_router(compliance.router)
app.include_router(contracts.router)

@app.get("/healthz")
def health():
    return {"ok": True}

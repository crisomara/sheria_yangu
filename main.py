"""
Sheria Yangu — Know Your Rights Uganda
FastAPI entry point. Exposes the pipeline as an HTTP API
so the Kaggle notebook can call it during the demo.
"""

import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import APIError
from pydantic import BaseModel
from typing import Optional
import uvicorn

from agents.orchestrator import OrchestratorAgent
from utils.session import new_session, get_session

app = FastAPI(
    title="Sheria Yangu",
    description="AI-powered legal document understanding for Ugandan citizens.",
    version="0.1.0",
)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    # Raised by config.get_api_key() when no key is configured — message is safe to surface.
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    # Covers auth failures, rate limits, and connection errors from the LLM provider.
    # Full detail is already logged server-side by uvicorn; don't echo internals to the client.
    return JSONResponse(
        status_code=502,
        content={"detail": "The upstream AI provider request failed. Check server logs and your API key/quota."},
    )


@app.exception_handler(json.JSONDecodeError)
async def json_decode_error_handler(request, exc: json.JSONDecodeError):
    # An agent's LLM response didn't come back as valid JSON.
    return JSONResponse(
        status_code=502,
        content={"detail": "The AI model returned a malformed response. Please retry."},
    )

# CORS — permissive for demo; tighten for any real deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────

class TextQueryRequest(BaseModel):
    text: str
    session_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    session_id: str
    document_type: str
    summary: str
    your_rights: list[str]
    risks: list[dict]       # [{clause, severity, legal_basis, plain_explanation}]
    deadlines: list[dict]   # [{description, date_mentioned, urgency}]
    next_steps: list[str]
    legal_referrals: list[dict]
    disclaimer: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "sheria_yangu"}


@app.post("/analyse/text", response_model=AnalysisResponse)
async def analyse_text(request: TextQueryRequest):
    """
    Accepts raw pasted text — a contract clause, a notice, a query.
    No file upload needed; ideal for the Kaggle notebook demo.
    """
    session_id = request.session_id or new_session()
    orchestrator = OrchestratorAgent(session_id=session_id)
    result = await orchestrator.run(document_text=request.text)
    return result


@app.post("/analyse/file", response_model=AnalysisResponse)
async def analyse_file(file: UploadFile = File(...)):
    """
    Accepts a PDF or .txt upload.
    Content is parsed in-memory; nothing is written to disk.
    """
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF and plain text files are supported."
        )

    session_id = new_session()
    raw_bytes = await file.read()
    orchestrator = OrchestratorAgent(session_id=session_id)
    result = await orchestrator.run(raw_bytes=raw_bytes, mime_type=file.content_type)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

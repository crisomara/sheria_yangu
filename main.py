"""
Sheria Yangu — Know Your Rights Uganda
FastAPI entry point. Exposes the pipeline as an HTTP API
so the Kaggle notebook can call it during the demo.
"""

import json

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import APIError
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import config
from agents.orchestrator import OrchestratorAgent
from utils.session import new_session

app = FastAPI(
    title="Sheria Yangu",
    description="AI-powered legal document understanding for Ugandan citizens.",
    version="0.1.0",
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
# Keyed by client IP. Protects the LLM-backed endpoints from a single client
# burning through the (often small, free-tier) LLM quota shared by everyone
# using this deployment. Configurable via RATE_LIMIT_PER_MINUTE in .env.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


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


# CORS — deny all cross-origin browser requests until ALLOWED_ORIGINS is set
# in .env. Does not affect non-browser clients (curl, the Kaggle notebook,
# requests/httpx) since CORS is a browser-only mechanism.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────


class TextQueryRequest(BaseModel):
    # max_length keeps a single request from burning excessive LLM tokens/quota;
    # a real notice/contract/summons is well under this. session_id is
    # deliberately NOT client-suppliable — always server-generated (see
    # utils/session.py) so a client can never reference someone else's session.
    text: str = Field(..., min_length=1, max_length=config.MAX_TEXT_LENGTH)


class AnalysisResponse(BaseModel):
    session_id: str
    document_type: str
    summary: str
    your_rights: list[str]
    risks: list[dict]  # [{clause, severity, legal_basis, plain_explanation}]
    deadlines: list[dict]  # [{description, date_mentioned, urgency}]
    next_steps: list[str]
    legal_referrals: list[dict]
    disclaimer: str


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sheria_yangu"}


@app.post("/analyse/text", response_model=AnalysisResponse)
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def analyse_text(request: Request, body: TextQueryRequest):
    """
    Accepts raw pasted text — a contract clause, a notice, a query.
    No file upload needed; ideal for the Kaggle notebook demo.
    """
    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id)
    result = await orchestrator.run(document_text=body.text)
    return result


@app.post("/analyse/file", response_model=AnalysisResponse)
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def analyse_file(request: Request, file: UploadFile = File(...)):
    """
    Accepts a PDF or .txt upload.
    Content is parsed in-memory; nothing is written to disk.
    """
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(status_code=415, detail="Only PDF and plain text files are supported.")

    raw_bytes = await _read_upload_within_limit(file)

    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id)
    result = await orchestrator.run(raw_bytes=raw_bytes, mime_type=file.content_type)
    return result


async def _read_upload_within_limit(file: UploadFile) -> bytes:
    """
    Reads an upload in chunks, aborting as soon as MAX_UPLOAD_BYTES is
    exceeded — never buffers an oversized file fully into memory first.
    """
    chunks = []
    total = 0
    chunk_size = 1024 * 1024  # 1 MB
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > config.MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the {config.MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

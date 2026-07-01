# Sheria Yangu — create all missing files
# Run this from inside your "sheria yangu" folder:
#   cd "C:\Users\User\Downloads\sheria yangu"
#   .\setup_files.ps1

Set-Location $PSScriptRoot

# Create missing folders
New-Item -ItemType Directory -Force -Path "mcp"
New-Item -ItemType Directory -Force -Path "utils"
New-Item -ItemType Directory -Force -Path "tests"
New-Item -ItemType Directory -Force -Path "notebooks"

# Empty __init__.py files
"" | Set-Content "agents\__init__.py"
"" | Set-Content "mcp\__init__.py"
"" | Set-Content "knowledge\__init__.py"
"" | Set-Content "utils\__init__.py"
"" | Set-Content "tests\__init__.py"

# ── agents\intake.py ──────────────────────────────────────────────────────────
@'
"""
Intake Agent — Sheria Yangu

Responsibilities:
  - Parse raw input (text or PDF bytes) into clean extracted text
  - Classify the document type (eviction notice, employment contract, etc.)
  - Extract key entities: parties, dates, monetary amounts, obligations

OUTPUT SCHEMA:
{
  "document_type": str,
  "extracted_text": str,
  "entities": {
    "parties": list[str],
    "dates": list[str],
    "amounts": list[str],
    "obligations": list[str],
    "jurisdiction": str
  }
}
"""

import json
import re
from typing import Optional
import google.generativeai as genai


INTAKE_SYSTEM_PROMPT = """You are the Intake Agent for Sheria Yangu, a legal document
understanding system for Ugandan citizens.

Your job is to read a legal document and extract structured information from it.
You do NOT interpret the law or give any legal opinion — that is handled by other agents.
Your only job is classification and entity extraction.

Always respond with valid JSON only. No preamble, no explanation outside the JSON.

Output this exact schema:
{
  "document_type": "<one of: Employment Contract, Eviction Notice, Police Summons,
                    Land Agreement, Court Order, Tenancy Agreement, Loan Agreement,
                    Government Notice, Other>",
  "extracted_text": "<the full cleaned text of the document>",
  "entities": {
    "parties": ["<party 1>", "<party 2>"],
    "dates": ["<date string as written in document>"],
    "amounts": ["<monetary or numerical amounts as written>"],
    "obligations": ["<explicit obligation stated in the document>"],
    "jurisdiction": "<country or region mentioned, default Uganda if not stated>"
  }
}

If the document is not in English, translate it to English first, then extract.
If any entity category is empty, return an empty list [].
"""


class IntakeAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=INTAKE_SYSTEM_PROMPT,
        )

    async def run(
        self,
        document_text: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        if document_text:
            text_to_analyse = document_text
        elif raw_bytes and mime_type == "application/pdf":
            text_to_analyse = self._extract_pdf_text(raw_bytes)
        elif raw_bytes and mime_type == "text/plain":
            text_to_analyse = raw_bytes.decode("utf-8", errors="replace")
        else:
            raise ValueError("IntakeAgent requires either document_text or raw_bytes.")

        response = self.model.generate_content(
            f"Please classify and extract entities from this document:\n\n{text_to_analyse}"
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        result = json.loads(raw)

        if not result.get("extracted_text"):
            result["extracted_text"] = text_to_analyse

        return result

    def _extract_pdf_text(self, raw_bytes: bytes) -> str:
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except Exception as e:
            return f"[PDF extraction failed: {e}. Please paste the document text directly.]"
'@ | Set-Content "agents\intake.py" -Encoding UTF8

# ── agents\research.py ────────────────────────────────────────────────────────
@'
"""
Research Agent — Sheria Yangu

Retrieves relevant Ugandan statutes for the document type.
Only surfaces what the law states — no interpretation.

OUTPUT SCHEMA:
{
  "statutes": [
    { "act": str, "section": str, "title": str, "text": str, "relevance": str }
  ]
}
"""

import json
import re
import google.generativeai as genai
from mcp.statute_lookup import lookup_statutes


RESEARCH_SYSTEM_PROMPT = """You are the Research Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens.

You have been given a document type, extracted entities, and statute excerpts from
the knowledge base. Select which statutes are DIRECTLY relevant to this document.
Do not invent statutes — only use what is provided.

For each relevant statute, write ONE sentence explaining why it applies.

Always respond with valid JSON only. No preamble, no explanation outside the JSON.

Output this exact schema:
{
  "statutes": [
    {
      "act": "<full act name and year>",
      "section": "<section number>",
      "title": "<section title>",
      "text": "<the statutory text excerpt>",
      "relevance": "<one sentence: why this applies to this specific document>"
    }
  ]
}

If no statute is relevant, return {"statutes": []}.
Maximum 6 statutes. Prioritise the most directly applicable ones.
"""


class ResearchAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=RESEARCH_SYSTEM_PROMPT,
        )

    async def run(self, document_type: str, extracted_text: str, entities: dict) -> dict:
        candidate_statutes = lookup_statutes(
            document_type=document_type,
            entities=entities,
        )

        if not candidate_statutes:
            return {"statutes": []}

        statutes_text = json.dumps(candidate_statutes, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.model.generate_content(
            f"Document type: {document_type}\n\n"
            f"Entities extracted:\n{entities_text}\n\n"
            f"Available statutes from knowledge base:\n{statutes_text}\n\n"
            "Select and annotate the relevant statutes."
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
'@ | Set-Content "agents\research.py" -Encoding UTF8

# ── agents\synthesis.py ───────────────────────────────────────────────────────
@'
"""
Synthesis Agent — Sheria Yangu

Produces the plain-language citizen-facing report.
Surfaces rights and options — never tells the citizen what to do.

GUARDRAIL: Legal information only, not legal advice.

OUTPUT SCHEMA:
{
  "summary": str,
  "your_rights": list[str],
  "next_steps": list[str]
}
"""

import json
import re
import google.generativeai as genai


SYNTHESIS_SYSTEM_PROMPT = """You are the Synthesis Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens. You write the citizen-facing report.

AUDIENCE: A Ugandan citizen with no legal training. Write clearly and simply.
Use short sentences. Avoid legal jargon. Write in the second person ("you", "your").

CRITICAL GUARDRAIL — NO LEGAL ADVICE:
You surface information and options. You never tell the citizen what to do.

PERMITTED next steps:
  "You have the right to request written reasons for this decision."
  "You may seek clarification on any clause before signing."
  "You can contact FIDA Uganda for free legal assistance."

NOT PERMITTED next steps:
  "You should refuse to sign."
  "File a complaint immediately."
  "Do not comply with this notice."

For "your_rights": state each right factually with its legal source.
For "next_steps": state options and information, not instructions.

Always respond with valid JSON only. No preamble, no explanation outside the JSON.

Output this exact schema:
{
  "summary": "<2-3 sentences: what this document is and what it means for the citizen>",
  "your_rights": ["<plain-language right with legal source>"],
  "next_steps": ["<factual option or information available to the citizen>"]
}
"""


class SynthesisAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYNTHESIS_SYSTEM_PROMPT,
        )

    async def run(self, document_type: str, entities: dict, analysis: dict) -> dict:
        analysis_text = json.dumps(analysis, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.model.generate_content(
            f"Document type: {document_type}\n\n"
            f"Entities (parties, dates, obligations):\n{entities_text}\n\n"
            f"Analysis results (risks, deadlines, rights gaps):\n{analysis_text}\n\n"
            "Write the plain-language citizen report."
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
'@ | Set-Content "agents\synthesis.py" -Encoding UTF8

# ── mcp\statute_lookup.py ─────────────────────────────────────────────────────
@'
"""
MCP Statute Lookup Tool — Sheria Yangu

Maps document types to relevant Ugandan statutory provisions.
Day 2: wrap this as a proper FastMCP server.
"""

from knowledge.uganda_statutes import STATUTE_DB


def lookup_statutes(document_type: str, entities: dict) -> list[dict]:
    doc_type_lower = document_type.lower()

    tag_map = {
        "employment contract":  ["employment", "labour", "termination"],
        "eviction notice":      ["tenancy", "landlord", "property"],
        "police summons":       ["police", "criminal", "rights", "arrest"],
        "land agreement":       ["land", "property", "registration"],
        "tenancy agreement":    ["tenancy", "landlord", "property"],
        "loan agreement":       ["financial", "contract", "interest"],
        "court order":          ["court", "criminal", "rights"],
        "government notice":    ["administrative", "rights"],
    }

    applicable_tags = set()
    for key, tags in tag_map.items():
        if key in doc_type_lower:
            applicable_tags.update(tags)

    if not applicable_tags:
        applicable_tags = {"rights", "constitutional"}

    applicable_tags.add("constitutional")

    results = [
        statute for statute in STATUTE_DB
        if any(tag in statute.get("tags", []) for tag in applicable_tags)
    ]

    return results[:10]
'@ | Set-Content "mcp\statute_lookup.py" -Encoding UTF8

# ── utils\session.py ──────────────────────────────────────────────────────────
@'
"""
Session management for Sheria Yangu.

SECURITY DESIGN:
- Sessions are UUID-keyed in-memory dicts only.
- No session data is written to disk or any database.
- Sessions expire after SESSION_TTL_SECONDS.
- The user document is processed and discarded within a single pipeline run.
"""

import uuid
import time
from typing import Optional

SESSION_TTL_SECONDS = 600

_sessions: dict[str, dict] = {}


def new_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"created_at": time.time(), "data": {}}
    _evict_expired()
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    _evict_expired()
    session = _sessions.get(session_id)
    if session is None:
        return None
    if time.time() - session["created_at"] > SESSION_TTL_SECONDS:
        del _sessions[session_id]
        return None
    return session["data"]


def update_session(session_id: str, key: str, value) -> None:
    session = _sessions.get(session_id)
    if session:
        session["data"][key] = value


def destroy_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def _evict_expired() -> None:
    now = time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s["created_at"] > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]
'@ | Set-Content "utils\session.py" -Encoding UTF8

# Also update agents\orchestrator.py to use Google API key env var name
(Get-Content "agents\orchestrator.py") `
    -replace 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY' |
    Set-Content "agents\orchestrator.py"

# Also update main.py to use Google API key env var name  
(Get-Content "main.py") `
    -replace 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY' |
    Set-Content "main.py"

Write-Host ""
Write-Host "Done. All missing files created." -ForegroundColor Green
Write-Host ""
Write-Host "Now run:"
Write-Host "  git add ."
Write-Host "  git commit -m 'Day 1: add missing agent files, swap to Google API'"
Write-Host "  git push"
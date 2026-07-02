# Sheria Yangu — Day 2 files
# Run from inside your "sheria yangu" folder:
#   cd "C:\Users\User\Downloads\sheria yangu"
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\day2_files.ps1

Set-Location $PSScriptRoot

# ── mcp\server.py — the custom MCP server ────────────────────────────────────
@'
"""
Sheria Yangu — Custom MCP Server

Exposes the Uganda statute knowledge base as proper MCP tools
using FastMCP. The Research Agent calls these tools instead of
importing lookup functions directly.

TOOLS EXPOSED:
  - lookup_statutes(document_type, context) -> list of statute dicts
  - list_acts()                             -> all Acts in the knowledge base
  - get_section(act_name, section)          -> one specific section

To run standalone: python -m mcp.server
"""

from fastmcp import FastMCP
from typing import Optional
from knowledge.uganda_statutes import STATUTE_DB

mcp = FastMCP(
    name="sheria-yangu-statutes",
    instructions=(
        "Provides access to a curated knowledge base of Ugandan statutory "
        "provisions. Use lookup_statutes to find relevant law for a given "
        "document type. Use list_acts to see all Acts covered."
    ),
)


@mcp.tool()
def lookup_statutes(document_type: str, context: Optional[str] = None) -> list[dict]:
    """
    Find Ugandan statutory provisions relevant to a given document type.

    Args:
        document_type: The type of legal document being analysed.
                       e.g. 'Employment Contract', 'Eviction Notice',
                       'Police Summons', 'Land Agreement', 'Loan Agreement'
        context:       Optional extra context to narrow the search.

    Returns:
        List of statute dicts with act, section, title, text, source_url, tags.
        Maximum 10 results. Always includes constitutional rights.
    """
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

    if context:
        context_lower = context.lower()
        if any(w in context_lower for w in ["fire", "dismiss", "terminat", "redundan"]):
            applicable_tags.update(["employment", "termination"])
        if any(w in context_lower for w in ["rent", "landlord", "tenant", "vacate"]):
            applicable_tags.update(["tenancy", "landlord"])
        if any(w in context_lower for w in ["arrest", "detain", "police", "charge"]):
            applicable_tags.update(["police", "criminal", "arrest"])
        if any(w in context_lower for w in ["land", "title", "mailo", "lease"]):
            applicable_tags.update(["land", "property"])

    results = [
        statute for statute in STATUTE_DB
        if any(tag in statute.get("tags", []) for tag in applicable_tags)
    ]

    return results[:10]


@mcp.tool()
def list_acts() -> list[str]:
    """
    List all Acts currently in the Sheria Yangu knowledge base.

    Returns:
        A deduplicated sorted list of Act names and years.
    """
    acts = sorted({statute["act"] for statute in STATUTE_DB})
    return acts


@mcp.tool()
def get_section(act_name: str, section: str) -> Optional[dict]:
    """
    Retrieve a specific section from a specific Act.

    Args:
        act_name: e.g. 'Employment Act 2006'
        section:  e.g. 'Section 58'

    Returns:
        The statute dict if found, or None.
    """
    for statute in STATUTE_DB:
        if (act_name.lower() in statute["act"].lower() and
                section.lower() in statute["section"].lower()):
            return statute
    return None


if __name__ == "__main__":
    mcp.run()
'@ | Set-Content "mcp\server.py" -Encoding UTF8

# ── agents\analysis.py — rewritten for Google AI ─────────────────────────────
@'
"""
Analysis Agent — Sheria Yangu

Compares what the document says against what the law says.
Identifies rights gaps, risks, and deadlines.

CRITICAL CONSTRAINT — factual comparison only:
  PERMITTED:  "The document states 7 days notice. The Employment Act requires 30 days."
  FORBIDDEN:  "You should reject this clause."
  FORBIDDEN:  "This contract is illegal."

OUTPUT SCHEMA:
{
  "risks": [
    {
      "clause": str,
      "severity": str,
      "what_document_says": str,
      "what_law_says": str,
      "legal_basis": str,
      "plain_explanation": str
    }
  ],
  "deadlines": [{ "description": str, "date_mentioned": str, "urgency": str }],
  "rights_gaps": [{ "right": str, "legal_basis": str, "status_in_document": str }]
}
"""

import json
import re
import google.generativeai as genai


ANALYSIS_SYSTEM_PROMPT = """You are the Analysis Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens.

CRITICAL RULE: Compare what documents say against what Ugandan law says.
You do NOT give legal advice. You do NOT tell the citizen what to do.
Surface factual comparisons only.

PERMITTED:
  "The document states 7 days notice. The Employment Act 2006 s.58 requires 30 days."
  "This clause waives a right granted by the Landlord and Tenant Act 2022."

NOT PERMITTED:
  "You should reject this clause."
  "This contract is illegal and you should not sign it."

Severity levels:
  HIGH   — clause likely contravenes a specific Ugandan statute
  MEDIUM — clause is ambiguous or potentially disadvantageous under law
  LOW    — clause is standard but the citizen should be aware of it

Always respond with valid JSON only. No preamble, no markdown fences.

Output this exact schema:
{
  "risks": [
    {
      "clause": "<brief quote or description of the clause>",
      "severity": "<HIGH|MEDIUM|LOW>",
      "what_document_says": "<factual: what this clause states>",
      "what_law_says": "<factual: what Ugandan law states on this point>",
      "legal_basis": "<Act name, section number>",
      "plain_explanation": "<one sentence a non-lawyer understands>"
    }
  ],
  "deadlines": [
    {
      "description": "<what this deadline is for>",
      "date_mentioned": "<as written in document>",
      "urgency": "<IMMEDIATE|SHORT_TERM|GENERAL>"
    }
  ],
  "rights_gaps": [
    {
      "right": "<the citizen right under Ugandan law>",
      "legal_basis": "<Act name, section>",
      "status_in_document": "<Not mentioned|Partially covered|Restricted>"
    }
  ]
}

If there are no items in a category return an empty list [].
"""


class AnalysisAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=ANALYSIS_SYSTEM_PROMPT,
        )

    async def run(
        self,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        """Core reasoning pass: document vs law comparison."""
        statutes_text = json.dumps(statutes, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.model.generate_content(
            f"DOCUMENT TEXT:\n{extracted_text}\n\n"
            f"ENTITIES EXTRACTED:\n{entities_text}\n\n"
            f"RELEVANT UGANDAN STATUTES:\n{statutes_text}\n\n"
            "Compare what the document says against what the law says. "
            "Identify risks, deadlines, and rights gaps."
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
'@ | Set-Content "agents\analysis.py" -Encoding UTF8

# ── agents\orchestrator.py — with progress logging ───────────────────────────
@'
"""
Orchestrator Agent — Sheria Yangu

Coordinates the four specialist agents:
  1. IntakeAgent    — classify document, extract entities
  2. ResearchAgent  — find relevant Ugandan law via MCP server
  3. AnalysisAgent  — identify rights gaps, risks, deadlines
  4. SynthesisAgent — produce plain-language citizen report

SECURITY: Session destroyed after every pipeline run.
No document content persists between requests.
"""

import os
import json
from typing import Optional

from agents.intake import IntakeAgent
from agents.research import ResearchAgent
from agents.analysis import AnalysisAgent
from agents.synthesis import SynthesisAgent
from utils.session import update_session, destroy_session

DISCLAIMER = (
    "Sheria Yangu provides legal information based on Ugandan law, "
    "not legal advice. For advice specific to your situation, consult "
    "a qualified advocate or contact the Uganda Law Society (0414-254848) "
    "or Legal Aid Service Providers Network (LASPNET)."
)

LEGAL_REFERRALS = [
    {
        "name": "Uganda Law Society",
        "phone": "0414-254848",
        "url": "https://www.ugandabar.or.ug",
        "notes": "Can refer you to a qualified advocate."
    },
    {
        "name": "FIDA Uganda",
        "phone": "0414-530848",
        "url": "https://www.fidauganda.org",
        "notes": "Free legal aid for women and vulnerable groups."
    },
    {
        "name": "LASPNET",
        "url": "https://www.laspnet.org",
        "notes": "Network of legal aid providers across Uganda."
    },
    {
        "name": "Uganda Human Rights Commission",
        "phone": "0800-200-500",
        "url": "https://www.uhrc.ug",
        "notes": "Toll-free. For human rights violations."
    },
]


class OrchestratorAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.api_key = os.environ.get("GOOGLE_API_KEY", "")

    async def run(
        self,
        document_text: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        """Run the full pipeline. Session destroyed after completion."""
        try:
            # Step 1: Intake
            print("[Orchestrator] Step 1: Intake agent...")
            intake = IntakeAgent(api_key=self.api_key)
            intake_result = await intake.run(
                document_text=document_text,
                raw_bytes=raw_bytes,
                mime_type=mime_type,
            )
            update_session(self.session_id, "intake", intake_result)
            print(f"[Orchestrator] Document type: {intake_result['document_type']}")

            # Step 2: Research
            print("[Orchestrator] Step 2: Research agent...")
            research = ResearchAgent(api_key=self.api_key)
            research_result = await research.run(
                document_type=intake_result["document_type"],
                extracted_text=intake_result["extracted_text"],
                entities=intake_result["entities"],
            )
            update_session(self.session_id, "research", research_result)
            print(f"[Orchestrator] Found {len(research_result['statutes'])} relevant statutes")

            # Step 3: Analysis
            print("[Orchestrator] Step 3: Analysis agent...")
            analysis = AnalysisAgent(api_key=self.api_key)
            analysis_result = await analysis.run(
                extracted_text=intake_result["extracted_text"],
                entities=intake_result["entities"],
                statutes=research_result["statutes"],
            )
            update_session(self.session_id, "analysis", analysis_result)
            print(f"[Orchestrator] Found {len(analysis_result['risks'])} risks, "
                  f"{len(analysis_result['deadlines'])} deadlines")

            # Step 4: Synthesis
            print("[Orchestrator] Step 4: Synthesis agent...")
            synthesis = SynthesisAgent(api_key=self.api_key)
            synthesis_result = await synthesis.run(
                document_type=intake_result["document_type"],
                entities=intake_result["entities"],
                analysis=analysis_result,
            )
            print("[Orchestrator] Pipeline complete.")

            return {
                "session_id": self.session_id,
                "document_type": intake_result["document_type"],
                "summary": synthesis_result["summary"],
                "your_rights": synthesis_result["your_rights"],
                "risks": analysis_result["risks"],
                "deadlines": analysis_result["deadlines"],
                "next_steps": synthesis_result["next_steps"],
                "legal_referrals": LEGAL_REFERRALS,
                "disclaimer": DISCLAIMER,
            }

        finally:
            destroy_session(self.session_id)
'@ | Set-Content "agents\orchestrator.py" -Encoding UTF8

# ── tests\test_pipeline.py — three real document scenarios ───────────────────
@'
"""
End-to-end pipeline test — Sheria Yangu Day 2

Three test scenarios:
  1. Eviction notice    (unlawful — 3 days, no reason)
  2. Employment clause  (below statutory notice period + leave)
  3. Police summons     (citizen rights check)

Run with:
  cd "sheria yangu"
  python -m tests.test_pipeline
"""

import asyncio
import os
from dotenv import load_dotenv
from utils.session import new_session
from agents.orchestrator import OrchestratorAgent

load_dotenv()

EVICTION_NOTICE = """
NOTICE TO VACATE

To: Mr. John Okello
    Plot 14, Nakawa Division, Kampala

From: Mr. Robert Ssemakula (Landlord)
Date: 1 July 2026

You are hereby required to vacate the above premises within THREE (3) DAYS
from the date of this notice.

Failure to vacate will result in your belongings being removed from the
premises and the locks being changed.

No reason is given for this notice.

Signed: R. Ssemakula
"""

EMPLOYMENT_CONTRACT_CLAUSE = """
TERMINATION CLAUSE — Employment Contract

Employee: Ms. Grace Atim
Employer: Kampala Trading Company Ltd

Section 7 — Termination:
The employer may terminate this contract at any time by giving the employee
FIVE (5) DAYS written notice, or payment in lieu thereof, regardless of
the employee's length of service.

The employee waives any right to claim unfair termination provided the
employer pays the 5-day notice pay.

Section 8 — Annual Leave:
The employee is entitled to 10 working days of annual leave per year.
"""

POLICE_SUMMONS = """
UGANDA POLICE FORCE
CENTRAL POLICE STATION, KAMPALA

SUMMONS TO ATTEND

To: Ms. Sarah Namukasa
    Wandegeya, Kampala

You are hereby summoned to appear at Central Police Station, Kampala
on 5 July 2026 at 9:00 AM.

You are required to answer questions in connection with a matter under
investigation. Failure to appear may result in your arrest.

You are not required to bring a lawyer.

Officer: D/Cpl James Opolot
Badge No: 4471
"""


async def run_test(name: str, document: str):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print("="*60)

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set. Add it to your .env file.")
        return

    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id)

    try:
        result = await orchestrator.run(document_text=document)

        print(f"\nDocument type : {result['document_type']}")
        print(f"\nSUMMARY:\n{result['summary']}")

        print(f"\nYOUR RIGHTS ({len(result['your_rights'])}):")
        for r in result["your_rights"]:
            print(f"  • {r}")

        print(f"\nRISKS ({len(result['risks'])}):")
        for risk in result["risks"]:
            print(f"  [{risk['severity']}] {risk['plain_explanation']}")
            print(f"    Document says : {risk['what_document_says']}")
            print(f"    Law says      : {risk['what_law_says']}")
            print(f"    Legal basis   : {risk['legal_basis']}")

        print(f"\nDEADLINES ({len(result['deadlines'])}):")
        for d in result["deadlines"]:
            print(f"  [{d['urgency']}] {d['description']} — {d['date_mentioned']}")

        print(f"\nNEXT STEPS ({len(result['next_steps'])}):")
        for step in result["next_steps"]:
            print(f"  • {step}")

        print(f"\nDISCLAIMER:\n{result['disclaimer']}")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


async def main():
    print("Sheria Yangu — End-to-End Pipeline Test")
    print("Day 2: First real run\n")
    await run_test("Eviction Notice", EVICTION_NOTICE)
    await run_test("Employment Contract Clause", EMPLOYMENT_CONTRACT_CLAUSE)
    await run_test("Police Summons", POLICE_SUMMONS)
    print(f"\n{'='*60}")
    print("All tests complete.")


if __name__ == "__main__":
    asyncio.run(main())
'@ | Set-Content "tests\test_pipeline.py" -Encoding UTF8

# ── requirements.txt — updated ────────────────────────────────────────────────
@'
google-generativeai>=0.8.0
fastmcp>=0.4.0
fastapi>=0.115.0
uvicorn>=0.32.0
pypdf>=4.0.0
python-multipart>=0.0.12
pydantic>=2.9.0
python-dotenv>=1.0.0
'@ | Set-Content "requirements.txt" -Encoding UTF8

Write-Host ""
Write-Host "Day 2 files created:" -ForegroundColor Green
Write-Host "  mcp\server.py          — custom MCP server (3 tools)"
Write-Host "  agents\analysis.py     — rewritten for Google AI"
Write-Host "  agents\orchestrator.py — with progress logging"
Write-Host "  tests\test_pipeline.py — 3 real document scenarios"
Write-Host "  requirements.txt       — updated dependencies"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Add your key to .env:  GOOGLE_API_KEY=your_key_here"
Write-Host "  2. Install dependencies:  pip install -r requirements.txt"
Write-Host "  3. Run the test:          python -m tests.test_pipeline"
Write-Host "  4. Commit and push:       git add . && git commit -m 'Day 2: MCP server + first pipeline test' && git push"

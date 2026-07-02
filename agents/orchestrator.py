"""
Orchestrator Agent — Sheria Yangu

Coordinates the four specialist agents in sequence:
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
        """
        Run the full pipeline. Session destroyed after completion.
        """
        try:
            # ── Step 1: Intake ────────────────────────────────────────
            print("[Orchestrator] Step 1: Intake agent...")
            intake = IntakeAgent(api_key=self.api_key)
            intake_result = await intake.run(
                document_text=document_text,
                raw_bytes=raw_bytes,
                mime_type=mime_type,
            )
            update_session(self.session_id, "intake", intake_result)
            print(f"[Orchestrator] Document type: {intake_result['document_type']}")

            # ── Step 2: Research ──────────────────────────────────────
            print("[Orchestrator] Step 2: Research agent...")
            research = ResearchAgent(api_key=self.api_key)
            research_result = await research.run(
                document_type=intake_result["document_type"],
                extracted_text=intake_result["extracted_text"],
                entities=intake_result["entities"],
            )
            update_session(self.session_id, "research", research_result)
            print(f"[Orchestrator] Found {len(research_result['statutes'])} relevant statutes")

            # ── Step 3: Analysis ──────────────────────────────────────
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

            # ── Step 4: Synthesis ─────────────────────────────────────
            print("[Orchestrator] Step 4: Synthesis agent...")
            synthesis = SynthesisAgent(api_key=self.api_key)
            synthesis_result = await synthesis.run(
                document_type=intake_result["document_type"],
                entities=intake_result["entities"],
                analysis=analysis_result,
            )
            print("[Orchestrator] Pipeline complete.")

            # ── Assemble final report ─────────────────────────────────
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
            # Always destroy session — no document content persists
            destroy_session(self.session_id)
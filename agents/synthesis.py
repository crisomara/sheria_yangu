"""
Synthesis Agent - Sheria Yangu

Produces the plain-language citizen-facing report.
GUARDRAIL: legal information only, never legal advice.
Uses google.genai (new SDK).
"""

import json
import re
from google import genai
from google.genai import types


SYNTHESIS_SYSTEM_PROMPT = """You are the Synthesis Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens. You write the citizen-facing report.

AUDIENCE: A Ugandan citizen with no legal training. Write clearly and simply.
Use short sentences. Avoid legal jargon. Write in the second person (you, your).

CRITICAL GUARDRAIL - NO LEGAL ADVICE:
You surface information and options. You never tell the citizen what to do.

PERMITTED next steps:
  You have the right to request written reasons for this decision.
  You may seek clarification on any clause before signing.
  You can contact FIDA Uganda for free legal assistance.

NOT PERMITTED next steps:
  You should refuse to sign.
  File a complaint immediately.
  Do not comply with this notice.

Always respond with valid JSON only. No preamble, no markdown fences.

Output this exact schema:
{
  "summary": "<2-3 sentences: what this document is and what it means for the citizen>",
  "your_rights": ["<plain-language right with legal source>"],
  "next_steps": ["<factual option or information available to the citizen>"]
}
"""


class SynthesisAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def run(self, document_type: str, entities: dict, analysis: dict) -> dict:
        analysis_text = json.dumps(analysis, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYNTHESIS_SYSTEM_PROMPT,
            ),
            contents=(
                f"Document type: {document_type}\n\n"
                f"Entities (parties, dates, obligations):\n{entities_text}\n\n"
                f"Analysis results (risks, deadlines, rights gaps):\n{analysis_text}\n\n"
                "Write the plain-language citizen report."
            )
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
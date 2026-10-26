"""
Synthesis Agent - Sheria Yangu
Produces the plain-language citizen-facing report.
GUARDRAIL: legal information only, never legal advice.
"""

import json
import re

from openai import OpenAI

from config import get_base_url, get_fallback_model, get_standard_model
from utils.llm import create_with_fallback

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
        self.client = OpenAI(
            base_url=get_base_url(),
            api_key=api_key,
        )
        self.model = get_standard_model()
        self.fallback = get_fallback_model()

    async def run(self, document_type: str, entities: dict, analysis: dict) -> dict:
        response = await create_with_fallback(
            self.client,
            self.model,
            self.fallback,
            messages=[
                {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Document type: {document_type}\n\n"
                        f"Entities (parties, dates, obligations):\n{json.dumps(entities, indent=2)}\n\n"
                        f"Analysis results (risks, deadlines, rights gaps):\n{json.dumps(analysis, indent=2)}\n\n"
                        "Write the plain-language citizen report."
                    ),
                },
            ],
            agent_label="Synthesis",
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

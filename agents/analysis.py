"""
Analysis Agent - Sheria Yangu

Compares what the document says against what the law says.
CRITICAL: factual comparison only, no legal advice.
Uses google.genai (new SDK).
"""

import json
import re
from google import genai
from google.genai import types


ANALYSIS_SYSTEM_PROMPT = """You are the Analysis Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens.

CRITICAL RULE: Compare what documents say against what Ugandan law says.
You do NOT give legal advice. You do NOT tell the citizen what to do.
Surface factual comparisons only.

PERMITTED:
  The document states 7 days notice. The Employment Act 2006 s.58 requires 30 days.
  This clause waives a right granted by the Landlord and Tenant Act 2022.

NOT PERMITTED:
  You should reject this clause.
  This contract is illegal and you should not sign it.

Severity levels:
  HIGH   - clause likely contravenes a specific Ugandan statute
  MEDIUM - clause is ambiguous or potentially disadvantageous under law
  LOW    - clause is standard but the citizen should be aware of it

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
        self.client = genai.Client(api_key=api_key)

    async def run(
        self,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        statutes_text = json.dumps(statutes, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=ANALYSIS_SYSTEM_PROMPT,
            ),
            contents=(
                f"DOCUMENT TEXT:\n{extracted_text}\n\n"
                f"ENTITIES EXTRACTED:\n{entities_text}\n\n"
                f"RELEVANT UGANDAN STATUTES:\n{statutes_text}\n\n"
                "Compare what the document says against what the law says. "
                "Identify risks, deadlines, and rights gaps."
            )
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
"""
Analysis Agent — Sheria Yangu

Responsibilities:
  - Compare what the document says against what the law says
  - Identify rights the citizen is entitled to vs what the document grants
  - Flag clauses that are potentially unlawful or disadvantageous
  - Detect time-sensitive deadlines
  - Assign risk severity levels

CRITICAL DESIGN CONSTRAINT — "what the document says vs what the law says":
This agent surfaces FACTUAL comparisons only:
  ✅ "The document states X days notice. The Employment Act requires Y days."
  ✅ "This clause restricts a right granted by Section Z of the Land Act."
  ❌ "You should reject this clause." — this is legal advice, not permitted.
  ❌ "This contract is illegal." — this is a legal conclusion, not permitted.

The analysis identifies gaps and tensions. The Synthesis Agent surfaces them
in plain language. Neither agent tells the citizen what to do.

OUTPUT SCHEMA:
{
  "risks": [
    {
      "clause": str,             # the problematic clause or section, quoted briefly
      "severity": str,           # "HIGH" | "MEDIUM" | "LOW"
      "what_document_says": str, # factual statement of what the document says
      "what_law_says": str,      # factual statement of what Ugandan law says
      "legal_basis": str,        # e.g. "Employment Act 2006, Section 58"
      "plain_explanation": str   # one sentence a non-lawyer can understand
    }
  ],
  "deadlines": [
    {
      "description": str,  # what the deadline relates to
      "date_mentioned": str,
      "urgency": str       # "IMMEDIATE" | "SHORT_TERM" | "GENERAL"
    }
  ],
  "rights_gaps": [
    {
      "right": str,        # the right the citizen has under Ugandan law
      "legal_basis": str,
      "status_in_document": str  # "Not mentioned" | "Partially covered" | "Restricted"
    }
  ]
}
"""

import json
import re

import anthropic


ANALYSIS_SYSTEM_PROMPT = """You are the Analysis Agent for Sheria Yangu, a legal 
document understanding system for Ugandan citizens.

CRITICAL RULE: You compare what documents say against what Ugandan law says.
You do NOT give legal advice. You do NOT tell the citizen what to do.
You surface factual comparisons only.

PERMITTED:
  "The document states 7 days notice. The Employment Act 2006 s.58 requires 30 days."
  "This clause waives a right granted by the Landlord and Tenant Act."

NOT PERMITTED:
  "You should reject this clause."
  "This contract is illegal and you should not sign it."
  "I recommend you consult a lawyer about clause 4." (synthesis agent handles referrals)

For each risk, classify severity:
  HIGH   — clause likely contravenes a specific Ugandan statute
  MEDIUM — clause is ambiguous, unusual, or potentially disadvantageous under law
  LOW    — clause is standard but the citizen should be aware of it

Always respond with valid JSON only. No preamble, no explanation outside the JSON.

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
      "right": "<the citizen's right under Ugandan law>",
      "legal_basis": "<Act name, section>",
      "status_in_document": "<Not mentioned|Partially covered|Restricted>"
    }
  ]
}

If there are no risks, deadlines, or rights gaps in a category, return an empty list.
"""


class AnalysisAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def run(
        self,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        """
        Core reasoning pass: document vs law comparison.
        """
        statutes_text = json.dumps(statutes, indent=2)
        entities_text = json.dumps(entities, indent=2)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"DOCUMENT TEXT:\n{extracted_text}\n\n"
                        f"ENTITIES EXTRACTED:\n{entities_text}\n\n"
                        f"RELEVANT UGANDAN STATUTES:\n{statutes_text}\n\n"
                        "Compare what the document says against what the law says. "
                        "Identify risks, deadlines, and rights gaps."
                    )
                }
            ]
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

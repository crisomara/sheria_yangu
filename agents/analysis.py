"""
Analysis Agent - Sheria Yangu

Compares what the document says against what the law says.
Uses the Antigravity reasoning model for deep legal comparison.

WHY ANTIGRAVITY HERE:
The analysis step is the most cognitively demanding in the pipeline.
It requires multi-step reasoning: read the document, read the statute,
identify gaps, classify severity, and produce structured output.
Antigravity's extended thinking capability is purpose-built for this.

Standard Gemini handles routine tasks (intake, research, synthesis).
Antigravity handles the critical legal reasoning step.

CRITICAL CONSTRAINT - factual comparison only, no legal advice:
  PERMITTED:  The document states 7 days notice. The Employment Act requires 30 days.
  FORBIDDEN:  You should reject this clause.
"""

import json
import re
from openai import OpenAI

# Primary: Antigravity reasoning model for deep legal analysis
ANTIGRAVITY_MODEL = "google/gemini-2.5-flash"  # swap to antigravity when quota available
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

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

Think through each clause carefully before classifying.
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
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = ANTIGRAVITY_MODEL

    async def run(
        self,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        """
        Core reasoning pass using Antigravity model.
        Falls back to standard model if Antigravity unavailable.
        """
        try:
            return await self._call_model(
                self.model, extracted_text, entities, statutes
            )
        except Exception as e:
            if "402" in str(e) or "404" in str(e):
                # Quota or model not found - fall back
                print(f"[Analysis] Antigravity unavailable ({e}), falling back...")
                return await self._call_model(
                    FALLBACK_MODEL, extracted_text, entities, statutes
                )
            raise

    async def _call_model(
        self,
        model: str,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"DOCUMENT TEXT:\n{extracted_text}\n\n"
                    f"ENTITIES EXTRACTED:\n{json.dumps(entities, indent=2)}\n\n"
                    f"RELEVANT UGANDAN STATUTES:\n{json.dumps(statutes, indent=2)}\n\n"
                    "Compare what the document says against what the law says. "
                    "Identify risks, deadlines, and rights gaps."
                )}
            ],
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

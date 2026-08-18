"""
Analysis Agent - Sheria Yangu

Compares what the document says against what the law says.

DEEP-REASONING ARCHITECTURE ("Antigravity" tier):
By default this agent uses gemini-3.1-pro-preview via the direct Google API
for deep legal comparison — Google is the default provider (see config.py).
That tier requires a billed Google Cloud project; without one, requests
automatically fall back to gemini-3.6-flash.

To use OpenAI/OpenRouter instead:
  Set USE_GOOGLE_API = False in config.py, and set OPENAI_API_KEY or
  OPENROUTER_API_KEY in your .env file.

The architecture, prompts, and output schema are identical across providers —
only the underlying model changes.

CRITICAL CONSTRAINT - factual comparison only, no legal advice:
  PERMITTED:  The document states 7 days notice. Employment Act requires 30 days.
  FORBIDDEN:  You should reject this clause.
"""

import json
import re
from openai import OpenAI
from config import get_base_url, get_reasoning_model, get_fallback_model, USE_GOOGLE_API

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
            base_url=get_base_url(),
            api_key=api_key,
        )
        # Production: Antigravity reasoning model
        # Demo: gemini-2.5-flash placeholder via OpenRouter
        self.model = get_reasoning_model()
        self.fallback = get_fallback_model()
        self.using_antigravity = USE_GOOGLE_API

    async def run(
        self,
        extracted_text: str,
        entities: dict,
        statutes: list[dict],
    ) -> dict:
        """
        Legal reasoning pass.
        Production: Antigravity model (extended thinking for complex legal comparison)
        Demo: Standard model placeholder with identical prompts and schema
        """
        model_label = "Antigravity" if self.using_antigravity else f"{self.model} (Antigravity placeholder)"
        print(f"[Analysis] Using model: {model_label}")

        try:
            return await self._call_model(
                self.model, extracted_text, entities, statutes
            )
        except Exception as e:
            if "402" in str(e) or "429" in str(e):
                print(f"[Analysis] Primary model unavailable, trying fallback...")
                return await self._call_model(
                    self.fallback, extracted_text, entities, statutes
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

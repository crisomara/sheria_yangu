"""
Research Agent â€” Sheria Yangu

Retrieves relevant Ugandan statutes for the document type.
Only surfaces what the law states â€” no interpretation.

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
Do not invent statutes â€” only use what is provided.

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

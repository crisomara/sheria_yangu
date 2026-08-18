"""
Research Agent - Sheria Yangu
Retrieves relevant Ugandan statutes via the MCP knowledge base.
"""

import json
import re
from openai import OpenAI
from fastmcp import Client
from config import get_base_url, get_standard_model
from mcp_tools.server import mcp as statute_mcp_server

RESEARCH_SYSTEM_PROMPT = """You are the Research Agent for Sheria Yangu, a legal
document understanding system for Ugandan citizens.

You have been given a document type, extracted entities, and statute excerpts from
the knowledge base. Select which statutes are DIRECTLY relevant to this document.
Do not invent statutes. Only use what is provided.

For each relevant statute, write ONE sentence explaining why it applies.

Always respond with valid JSON only. No preamble, no markdown fences.

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
        self.client = OpenAI(
            base_url=get_base_url(),
            api_key=api_key,
        )
        self.model = get_standard_model()

    async def run(self, document_type: str, extracted_text: str, entities: dict) -> dict:
        candidate_statutes = await self._lookup_statutes_via_mcp(
            document_type=document_type,
            entities=entities,
        )

        if not candidate_statutes:
            return {"statutes": []}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Document type: {document_type}\n\n"
                    f"Entities extracted:\n{json.dumps(entities, indent=2)}\n\n"
                    f"Available statutes from knowledge base:\n{json.dumps(candidate_statutes, indent=2)}\n\n"
                    "Select and annotate the relevant statutes."
                )}
            ],
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

    async def _lookup_statutes_via_mcp(self, document_type: str, entities: dict) -> list[dict]:
        """Calls the lookup_statutes tool on the real MCP server (in-process transport)."""
        context_terms = entities.get("obligations", []) + entities.get("parties", [])
        context = " ".join(context_terms) if context_terms else None

        async with Client(statute_mcp_server) as client:
            result = await client.call_tool(
                "lookup_statutes",
                {"document_type": document_type, "context": context},
            )
            return result.data

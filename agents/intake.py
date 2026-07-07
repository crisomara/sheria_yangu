"""
Intake Agent - Sheria Yangu
Classifies document type and extracts key entities.
"""

import json
import re
from typing import Optional
from openai import OpenAI
from config import get_api_key, get_base_url, get_standard_model

INTAKE_SYSTEM_PROMPT = """You are the Intake Agent for Sheria Yangu, a legal document
understanding system for Ugandan citizens.

Your job is to read a legal document and extract structured information from it.
You do NOT interpret the law or give any legal opinion.
Your only job is classification and entity extraction.

Always respond with valid JSON only. No preamble, no markdown fences.

Output this exact schema:
{
  "document_type": "<one of: Employment Contract, Eviction Notice, Police Summons, Land Agreement, Court Order, Tenancy Agreement, Loan Agreement, Government Notice, Other>",
  "extracted_text": "<the full cleaned text of the document>",
  "entities": {
    "parties": ["<party 1>", "<party 2>"],
    "dates": ["<date string as written in document>"],
    "amounts": ["<monetary or numerical amounts as written>"],
    "obligations": ["<explicit obligation stated in the document>"],
    "jurisdiction": "<country or region mentioned, default Uganda if not stated>"
  }
}

If any entity category is empty, return an empty list [].
"""


class IntakeAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url=get_base_url(),
            api_key=api_key,
        )
        self.model = get_standard_model()

    async def run(
        self,
        document_text: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        if document_text:
            text = document_text
        elif raw_bytes and mime_type == "application/pdf":
            text = self._extract_pdf_text(raw_bytes)
        elif raw_bytes and mime_type == "text/plain":
            text = raw_bytes.decode("utf-8", errors="replace")
        else:
            raise ValueError("IntakeAgent requires document_text or raw_bytes.")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify and extract entities from this document:\n\n{text}"}
            ],
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        result = json.loads(raw)

        if not result.get("extracted_text"):
            result["extracted_text"] = text

        return result

    def _extract_pdf_text(self, raw_bytes: bytes) -> str:
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except Exception as e:
            return f"[PDF extraction failed: {e}. Please paste the document text directly.]"

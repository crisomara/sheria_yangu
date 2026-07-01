"""
Intake Agent â€” Sheria Yangu

Responsibilities:
  - Parse raw input (text or PDF bytes) into clean extracted text
  - Classify the document type (eviction notice, employment contract, etc.)
  - Extract key entities: parties, dates, monetary amounts, obligations

OUTPUT SCHEMA:
{
  "document_type": str,
  "extracted_text": str,
  "entities": {
    "parties": list[str],
    "dates": list[str],
    "amounts": list[str],
    "obligations": list[str],
    "jurisdiction": str
  }
}
"""

import json
import re
from typing import Optional
import google.generativeai as genai


INTAKE_SYSTEM_PROMPT = """You are the Intake Agent for Sheria Yangu, a legal document
understanding system for Ugandan citizens.

Your job is to read a legal document and extract structured information from it.
You do NOT interpret the law or give any legal opinion â€” that is handled by other agents.
Your only job is classification and entity extraction.

Always respond with valid JSON only. No preamble, no explanation outside the JSON.

Output this exact schema:
{
  "document_type": "<one of: Employment Contract, Eviction Notice, Police Summons,
                    Land Agreement, Court Order, Tenancy Agreement, Loan Agreement,
                    Government Notice, Other>",
  "extracted_text": "<the full cleaned text of the document>",
  "entities": {
    "parties": ["<party 1>", "<party 2>"],
    "dates": ["<date string as written in document>"],
    "amounts": ["<monetary or numerical amounts as written>"],
    "obligations": ["<explicit obligation stated in the document>"],
    "jurisdiction": "<country or region mentioned, default Uganda if not stated>"
  }
}

If the document is not in English, translate it to English first, then extract.
If any entity category is empty, return an empty list [].
"""


class IntakeAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=INTAKE_SYSTEM_PROMPT,
        )

    async def run(
        self,
        document_text: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        if document_text:
            text_to_analyse = document_text
        elif raw_bytes and mime_type == "application/pdf":
            text_to_analyse = self._extract_pdf_text(raw_bytes)
        elif raw_bytes and mime_type == "text/plain":
            text_to_analyse = raw_bytes.decode("utf-8", errors="replace")
        else:
            raise ValueError("IntakeAgent requires either document_text or raw_bytes.")

        response = self.model.generate_content(
            f"Please classify and extract entities from this document:\n\n{text_to_analyse}"
        )

        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        result = json.loads(raw)

        if not result.get("extracted_text"):
            result["extracted_text"] = text_to_analyse

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

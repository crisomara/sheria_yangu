"""
Intake Agent - Sheria Yangu
Classifies document type and extracts key entities.
"""

import io
from typing import Optional

from openai import OpenAI
from pypdf import PdfReader

from config import get_base_url, get_fallback_model, get_standard_model
from utils.errors import UnreadableDocumentError
from utils.llm import create_with_fallback, parse_agent_json
from utils.schemas import IntakeOutput

NO_TEXT_MESSAGE = (
    "No readable text was found in this document. If it is a scan or a photo, paste the text of the document instead."
)
BAD_PDF_MESSAGE = "This PDF could not be opened. Check the file, or paste the text of the document instead."

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
        self.fallback = get_fallback_model()

    async def run(
        self,
        document_text: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> dict:
        if document_text:
            text = document_text
        elif raw_bytes is not None and mime_type == "application/pdf":
            text = self._extract_pdf_text(raw_bytes)
        elif raw_bytes is not None and mime_type == "text/plain":
            text = raw_bytes.decode("utf-8", errors="replace")
        elif document_text is not None:
            text = document_text
        else:
            raise ValueError("IntakeAgent requires document_text or raw_bytes.")

        # A scan with no text layer, an empty upload or whitespace has nothing to
        # analyse. Stop here, before any model call is paid for.
        if not text.strip():
            raise UnreadableDocumentError(NO_TEXT_MESSAGE)

        response = await create_with_fallback(
            self.client,
            self.model,
            self.fallback,
            messages=[
                {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify and extract entities from this document:\n\n{text}"},
            ],
            agent_label="Intake",
        )

        result = parse_agent_json(response, IntakeOutput, agent_label="Intake")

        if not result["extracted_text"].strip():
            result["extracted_text"] = text

        return result

    def _extract_pdf_text(self, raw_bytes: bytes) -> str:
        """Returns the text layer of a PDF. Raises UnreadableDocumentError if the file cannot be parsed."""
        try:
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as e:  # noqa: BLE001 - pypdf raises many error types for a damaged file
            raise UnreadableDocumentError(BAD_PDF_MESSAGE) from e
        return "\n\n".join(pages).strip()

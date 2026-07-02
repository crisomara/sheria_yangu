import json, re, os
from typing import Optional
from google import genai
from google.genai import types

INTAKE_SYSTEM_PROMPT = '''You are the Intake Agent for Sheria Yangu, a legal document understanding system for Ugandan citizens. Your job is to classify the document and extract entities. Do NOT interpret law. Always respond with valid JSON only, no markdown fences.

Output this exact schema:
{
  "document_type": "<one of: Employment Contract, Eviction Notice, Police Summons, Land Agreement, Court Order, Tenancy Agreement, Loan Agreement, Government Notice, Other>",
  "extracted_text": "<full cleaned text>",
  "entities": {
    "parties": ["<party 1>"],
    "dates": ["<dates as written>"],
    "amounts": ["<amounts as written>"],
    "obligations": ["<obligations stated>"],
    "jurisdiction": "<default Uganda>"
  }
}'''

class IntakeAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def run(self, document_text=None, raw_bytes=None, mime_type=None):
        if document_text:
            text = document_text
        elif raw_bytes and mime_type == 'text/plain':
            text = raw_bytes.decode('utf-8', errors='replace')
        else:
            raise ValueError('IntakeAgent requires document_text or raw_bytes.')

        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(system_instruction=INTAKE_SYSTEM_PROMPT),
            contents=f'Classify and extract entities from this document:\n\n{text}'
        )
        raw = re.sub(r'^+json\s*|+$', '', response.text.strip(), flags=re.MULTILINE).strip()
        result = json.loads(raw)
        if not result.get('extracted_text'):
            result['extracted_text'] = text
        return result

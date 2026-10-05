"""Offline tests for the LLM fallback helper and agent response parsing.

A fake client stands in for the OpenAI SDK, so no network call or API key is needed.
"""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from openai import APIStatusError

from agents.intake import IntakeAgent
from utils.llm import create_with_fallback


def _status_error(code: int) -> APIStatusError:
    request = httpx.Request("POST", "https://example.invalid/v1/chat/completions")
    return APIStatusError("error", response=httpx.Response(code, request=request), body=None)


def _completion(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class FakeClient:
    """Mimics client.chat.completions.create, failing for models listed in `fail`."""

    def __init__(self, content: str = "{}", fail: dict | None = None):
        self.content = content
        self.fail = fail or {}
        self.calls: list[str] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages):
        self.calls.append(model)
        if model in self.fail:
            raise _status_error(self.fail[model])
        return _completion(self.content)


@pytest.mark.parametrize("code", [402, 429])
def test_fallback_on_quota_errors(code):
    client = FakeClient(fail={"primary": code})
    asyncio.run(create_with_fallback(client, "primary", "fallback", messages=[], agent_label="t"))
    assert client.calls == ["primary", "fallback"]


def test_no_fallback_on_other_errors():
    client = FakeClient(fail={"primary": 401})
    with pytest.raises(APIStatusError):
        asyncio.run(create_with_fallback(client, "primary", "fallback", messages=[], agent_label="t"))
    assert client.calls == ["primary"]


def _intake_with(content: str) -> IntakeAgent:
    agent = IntakeAgent(api_key="test-key-not-used")
    agent.client = FakeClient(content=content)
    return agent


def test_intake_parses_fenced_json_and_backfills_text():
    payload = {"document_type": "Eviction Notice", "extracted_text": "", "entities": {"parties": []}}
    agent = _intake_with("```json\n" + json.dumps(payload) + "\n```")
    result = asyncio.run(agent.run(document_text="Vacate in 3 days."))
    assert result["document_type"] == "Eviction Notice"
    assert result["extracted_text"] == "Vacate in 3 days."


def test_intake_decodes_plain_text_upload():
    payload = {"document_type": "Other", "extracted_text": "x", "entities": {}}
    agent = _intake_with(json.dumps(payload))
    result = asyncio.run(agent.run(raw_bytes=b"hello", mime_type="text/plain"))
    assert result["document_type"] == "Other"


def test_intake_requires_some_input():
    agent = _intake_with("{}")
    with pytest.raises(ValueError):
        asyncio.run(agent.run())


def test_pdf_extraction_failure_is_reported_not_raised():
    agent = _intake_with("{}")
    text = agent._extract_pdf_text(b"not a pdf")
    assert text.startswith("[PDF extraction failed")

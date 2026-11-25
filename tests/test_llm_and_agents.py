"""Offline tests for the LLM helpers, the agent output schemas and the Intake Agent.

A fake client stands in for the OpenAI SDK, so no network call or API key is needed.
"""

import asyncio
import io
import json
from types import SimpleNamespace

import httpx
import pytest
from openai import APIStatusError
from pypdf import PdfWriter

from agents.intake import IntakeAgent
from utils.errors import ModelOutputError, UnreadableDocumentError
from utils.llm import create_with_fallback, parse_agent_json
from utils.schemas import AnalysisOutput, IntakeOutput, ResearchOutput, SynthesisOutput


def _status_error(code: int) -> APIStatusError:
    request = httpx.Request("POST", "https://example.invalid/v1/chat/completions")
    return APIStatusError("error", response=httpx.Response(code, request=request), body=None)


def _completion(content):
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


def _blank_pdf() -> bytes:
    """A valid one-page PDF with no text layer, like a scan or a photo."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


# ── Fallback ──────────────────────────────────────────────────────────────────


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


# ── Reading and checking a model reply ────────────────────────────────────────

INTAKE_OK = {"document_type": "Eviction Notice", "extracted_text": "Vacate.", "entities": {"parties": ["A", "B"]}}


def test_parse_accepts_plain_and_fenced_json():
    plain = parse_agent_json(_completion(json.dumps(INTAKE_OK)), IntakeOutput, "Intake")
    fenced = parse_agent_json(_completion("```json\n" + json.dumps(INTAKE_OK) + "\n```"), IntakeOutput, "Intake")
    assert plain == fenced
    assert plain["document_type"] == "Eviction Notice"
    assert plain["entities"]["parties"] == ["A", "B"]
    assert plain["entities"]["obligations"] == []
    assert plain["entities"]["jurisdiction"] == "Uganda"


@pytest.mark.parametrize(
    "content",
    [
        None,  # the provider returned no text at all
        "",
        "   ",
        "Sorry, I cannot help with that.",  # prose, not JSON
        "[]",  # JSON, but not an object
        "{}",  # an object with the required key missing
        json.dumps({"document_type": "", "entities": {}}),
        json.dumps({"document_type": "Other", "entities": "none"}),
        json.dumps({"document_type": "Other", "entities": {"parties": [{"name": "A"}]}}),
    ],
)
def test_parse_rejects_replies_the_pipeline_cannot_use(content):
    with pytest.raises(ModelOutputError):
        parse_agent_json(_completion(content), IntakeOutput, "Intake")


def test_parse_rejects_a_response_with_no_choices():
    with pytest.raises(ModelOutputError):
        parse_agent_json(SimpleNamespace(choices=[]), IntakeOutput, "Intake")


def test_parse_error_names_the_field_and_never_quotes_the_reply():
    secret = "TENANT NAME AND ADDRESS"
    reply = json.dumps({"document_type": "Other", "entities": {"parties": [{"name": secret}]}})
    with pytest.raises(ModelOutputError) as error:
        parse_agent_json(_completion(reply), IntakeOutput, "Intake")
    assert "entities.parties" in str(error.value)
    assert secret not in str(error.value)


def test_schemas_accept_harmless_variations():
    intake = parse_agent_json(
        _completion(json.dumps({"document_type": "Loan Agreement", "entities": {"amounts": [500000, "UGX 2m"]}})),
        IntakeOutput,
        "Intake",
    )
    assert intake["entities"]["amounts"] == ["500000", "UGX 2m"]
    assert intake["extracted_text"] == ""

    analysis = parse_agent_json(
        _completion(
            json.dumps(
                {
                    "risks": [{"clause": "3 days notice", "severity": "high", "extra_key": "dropped"}],
                    "deadlines": [{"description": "Vacate", "date_mentioned": None, "urgency": "short term"}],
                    "rights_gaps": None,
                }
            )
        ),
        AnalysisOutput,
        "Analysis",
    )
    assert analysis["risks"][0]["severity"] == "HIGH"
    assert "extra_key" not in analysis["risks"][0]
    assert analysis["deadlines"][0] == {"description": "Vacate", "date_mentioned": "", "urgency": "SHORT_TERM"}
    assert analysis["rights_gaps"] == []

    assert parse_agent_json(_completion('{"statutes": null}'), ResearchOutput, "Research") == {"statutes": []}

    synthesis = parse_agent_json(
        _completion(json.dumps({"summary": "An eviction notice.", "your_rights": "One right.", "next_steps": None})),
        SynthesisOutput,
        "Synthesis",
    )
    assert synthesis == {"summary": "An eviction notice.", "your_rights": ["One right."], "next_steps": []}


@pytest.mark.parametrize(
    "schema, reply",
    [
        # A severity outside the three levels is not guessed at.
        (AnalysisOutput, {"risks": [{"clause": "x", "severity": "CATASTROPHIC"}]}),
        (AnalysisOutput, {"risks": [{"clause": "x"}]}),
        (AnalysisOutput, {"risks": "none"}),
        (ResearchOutput, {"statutes": [{"section": "Section 58"}]}),
        (SynthesisOutput, {"your_rights": [], "next_steps": []}),
        (SynthesisOutput, {"summary": "ok", "your_rights": [{"right": "x"}]}),
    ],
)
def test_schemas_reject_replies_that_would_change_the_report(schema, reply):
    with pytest.raises(ModelOutputError):
        parse_agent_json(_completion(json.dumps(reply)), schema, "agent")


# ── Intake Agent ──────────────────────────────────────────────────────────────


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


def test_intake_rejects_a_reply_in_the_wrong_shape():
    agent = _intake_with("{}")
    with pytest.raises(ModelOutputError):
        asyncio.run(agent.run(document_text="Vacate in 3 days."))


def test_damaged_pdf_is_refused():
    agent = _intake_with(json.dumps(INTAKE_OK))
    with pytest.raises(UnreadableDocumentError):
        agent._extract_pdf_text(b"not a pdf")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"raw_bytes": b"not a pdf", "mime_type": "application/pdf"},
        {"raw_bytes": b"", "mime_type": "application/pdf"},
        {"raw_bytes": _blank_pdf(), "mime_type": "application/pdf"},  # a scan: opens, but holds no text
        {"raw_bytes": b"", "mime_type": "text/plain"},
        {"raw_bytes": b"  \n\t ", "mime_type": "text/plain"},
        {"document_text": "   \n  "},
        {"document_text": ""},
    ],
)
def test_documents_with_no_readable_text_never_reach_the_model(kwargs):
    agent = _intake_with(json.dumps(INTAKE_OK))
    with pytest.raises(UnreadableDocumentError):
        asyncio.run(agent.run(**kwargs))
    assert agent.client.calls == []

"""FastAPI tests for main.py. None of these reach an LLM provider.

The first group covers the health check, security headers, input validation and
the no-key error path. The second group runs the whole pipeline against a fake
provider that answers each agent with a canned reply.
"""

import io
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

import agents.analysis
import agents.intake
import agents.research
import agents.synthesis
import config
import main


@pytest.fixture
def client(monkeypatch):
    # Rate limiting is covered by slowapi itself; disable it so test order can't trip it.
    monkeypatch.setattr(main.limiter, "enabled", False)
    return TestClient(main.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sheria_yangu"}


def test_security_headers(client):
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_empty_text_is_rejected(client):
    assert client.post("/analyse/text", json={"text": ""}).status_code == 422


def test_overlong_text_is_rejected(client):
    body = {"text": "a" * (config.MAX_TEXT_LENGTH + 1)}
    assert client.post("/analyse/text", json=body).status_code == 422


def test_unsupported_file_type_is_rejected(client):
    files = {"file": ("x.png", b"\x89PNG", "image/png")}
    assert client.post("/analyse/file", files=files).status_code == 415


def test_oversized_upload_is_rejected(client, monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 16)
    files = {"file": ("big.txt", b"x" * 64, "text/plain")}
    assert client.post("/analyse/file", files=files).status_code == 413


def test_missing_api_key_returns_clear_error(client, monkeypatch):
    monkeypatch.setattr(config, "USE_GOOGLE_API", True)
    monkeypatch.setattr(config, "GOOGLE_API_KEY", "")
    response = client.post("/analyse/text", json={"text": "Notice to vacate in 3 days."})
    assert response.status_code == 500
    assert "GOOGLE_API_KEY" in response.json()["detail"]


# ── The whole pipeline against a fake provider ────────────────────────────────

EVICTION_NOTICE = "NOTICE TO VACATE. You are required to vacate the premises within THREE (3) DAYS. Signed, Landlord."

REPLIES = {
    "Intake": {
        "document_type": "Eviction Notice",
        "extracted_text": "",
        "entities": {
            "parties": ["Landlord", "Tenant"],
            "dates": [],
            "amounts": [],
            "obligations": ["Vacate the premises within 3 days"],
            "jurisdiction": "Uganda",
        },
    },
    "Research": {
        "statutes": [
            {
                "act": "The Landlord and Tenant Act, 2022",
                "section": "Section 38",
                "title": "Termination after notice",
                "text": "In the case of a monthly tenancy; thirty days' notice.",
                "relevance": "Sets the notice a landlord must give.",
            }
        ]
    },
    "Analysis": {
        "risks": [
            {
                "clause": "Vacate within 3 days",
                "severity": "high",
                "what_document_says": "Three days to vacate.",
                "what_law_says": "Thirty days for a monthly tenancy.",
                "legal_basis": "The Landlord and Tenant Act, 2022, Section 38",
                "plain_explanation": "The notice is shorter than the law allows.",
            }
        ],
        "deadlines": [{"description": "Date to vacate", "date_mentioned": None, "urgency": "immediate"}],
        "rights_gaps": None,
    },
    "Synthesis": {
        "summary": "This is a notice asking you to leave your home.",
        "your_rights": ["You are entitled to the notice period set by law."],
        "next_steps": ["You may ask the landlord for the notice in writing."],
    },
}


class FakeProvider:
    """Stands in for the OpenAI client of every agent and answers by agent name."""

    def __init__(self):
        self.replies = dict(REPLIES)
        self.calls: list[str] = []
        self.prompts: dict[str, str] = {}
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages):
        system_prompt = messages[0]["content"]
        agent = next(name for name in REPLIES if f"{name} Agent" in system_prompt)
        self.calls.append(agent)
        self.prompts[agent] = messages[1]["content"]
        reply = self.replies[agent]
        content = reply if reply is None or isinstance(reply, str) else json.dumps(reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def provider(monkeypatch):
    fake = FakeProvider()
    for module in (agents.intake, agents.research, agents.analysis, agents.synthesis):
        monkeypatch.setattr(module, "OpenAI", lambda **kwargs: fake)
    monkeypatch.setattr(config, "USE_GOOGLE_API", True)
    monkeypatch.setattr(config, "GOOGLE_API_KEY", "test-key-not-used")
    return fake


def _blank_pdf() -> bytes:
    """A valid one-page PDF with no text layer, like a scan or a photo."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_pipeline_returns_a_checked_report(client, provider):
    response = client.post("/analyse/text", json={"text": EVICTION_NOTICE})
    assert response.status_code == 200
    assert provider.calls == ["Intake", "Research", "Analysis", "Synthesis"]

    report = response.json()
    assert report["document_type"] == "Eviction Notice"
    assert report["summary"] == REPLIES["Synthesis"]["summary"]
    # Values are normalised on the way through: "high" and a null date.
    assert report["risks"][0]["severity"] == "HIGH"
    assert report["deadlines"] == [{"description": "Date to vacate", "date_mentioned": "", "urgency": "IMMEDIATE"}]
    assert len(report["legal_referrals"]) == 4


def test_research_agent_is_given_the_governing_sections(client, provider):
    client.post("/analyse/text", json={"text": EVICTION_NOTICE})
    offered = provider.prompts["Research"]
    assert "Unlawful eviction of tenant" in offered  # Landlord and Tenant Act s.45
    assert "Termination after notice" in offered  # Landlord and Tenant Act s.38
    assert "Employment Act" not in offered


@pytest.mark.parametrize(
    "upload",
    [
        ("broken.pdf", b"this is not a pdf", "application/pdf"),
        ("scan.pdf", _blank_pdf(), "application/pdf"),
        ("empty.pdf", b"", "application/pdf"),
        ("empty.txt", b"", "text/plain"),
        ("spaces.txt", b" \n\t ", "text/plain"),
    ],
)
def test_unreadable_upload_is_refused_before_any_model_call(client, provider, upload):
    response = client.post("/analyse/file", files={"file": upload})
    assert response.status_code == 422
    assert "paste the text" in response.json()["detail"]
    assert provider.calls == []


def test_whitespace_only_text_is_refused_before_any_model_call(client, provider):
    response = client.post("/analyse/text", json={"text": "   \n  "})
    assert response.status_code == 422
    assert provider.calls == []


def test_readable_pdf_text_reaches_the_intake_agent(client, provider, monkeypatch):
    monkeypatch.setattr(agents.intake.IntakeAgent, "_extract_pdf_text", lambda self, raw: EVICTION_NOTICE)
    response = client.post("/analyse/file", files={"file": ("notice.pdf", b"%PDF-1.4", "application/pdf")})
    assert response.status_code == 200
    assert "THREE (3) DAYS" in provider.prompts["Intake"]


@pytest.mark.parametrize(
    "agent, reply, calls_made",
    [
        ("Intake", {}, ["Intake"]),
        ("Intake", None, ["Intake"]),
        ("Intake", "I could not read this document.", ["Intake"]),
        ("Research", {"statutes": [{"section": "Section 38"}]}, ["Intake", "Research"]),
        ("Analysis", {"risks": [{"clause": "x", "severity": "SEVERE"}]}, ["Intake", "Research", "Analysis"]),
        ("Synthesis", {"summary": None}, ["Intake", "Research", "Analysis", "Synthesis"]),
        (
            "Synthesis",
            {"summary": "ok", "your_rights": [{"right": "a right"}], "next_steps": []},
            ["Intake", "Research", "Analysis", "Synthesis"],
        ),
    ],
)
def test_model_reply_in_the_wrong_shape_returns_502(client, provider, agent, reply, calls_made):
    provider.replies[agent] = reply
    response = client.post("/analyse/text", json={"text": EVICTION_NOTICE})
    assert response.status_code == 502
    assert response.json() == {"detail": "The AI model returned a malformed response. Please retry."}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    # The pipeline stops at the stage that failed.
    assert provider.calls == calls_made


def test_unexpected_error_still_answers_in_json_with_security_headers(provider, monkeypatch):
    async def explode(self, **kwargs):
        raise RuntimeError("details that must not reach the client")

    monkeypatch.setattr(main.limiter, "enabled", False)
    monkeypatch.setattr(main.OrchestratorAgent, "run", explode)
    client = TestClient(main.app, raise_server_exceptions=False)

    response = client.post("/analyse/text", json={"text": EVICTION_NOTICE})
    assert response.status_code == 500
    assert response.json() == {"detail": "Something went wrong on the server. Please retry."}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"

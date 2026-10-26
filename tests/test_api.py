"""FastAPI tests for main.py. None of these reach an LLM provider: they cover the
health check, security headers, input validation, and the no-key error path."""

import pytest
from fastapi.testclient import TestClient

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

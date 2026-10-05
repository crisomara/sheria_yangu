"""Live end-to-end pipeline test against a real LLM provider.

Skipped unless GOOGLE_API_KEY is set in the environment. CI never sets it, so this
only runs when a developer opts in locally, e.g.:

    GOOGLE_API_KEY=... pytest -m live
"""

import asyncio
import os

import pytest

from agents.orchestrator import OrchestratorAgent
from tests.test_pipeline import EVICTION_NOTICE
from utils.session import new_session

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set"),
]


def test_eviction_notice_end_to_end():
    orchestrator = OrchestratorAgent(session_id=new_session())
    result = asyncio.run(orchestrator.run(document_text=EVICTION_NOTICE))
    for key in ("document_type", "summary", "your_rights", "risks", "deadlines", "next_steps"):
        assert key in result
    assert result["disclaimer"]

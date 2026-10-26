"""Smoke test: the Streamlit demo renders its initial page without errors.

No key is entered, so the page never builds an orchestrator or calls a model.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"


def test_streamlit_app_renders():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    assert not at.exception

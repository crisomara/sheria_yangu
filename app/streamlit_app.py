"""
Sheria Yangu — Streamlit demo, bring-your-own-key.

Every /analyse call is a real LLM spend (unlike a typical ML demo with zero
per-request inference cost), so this demo never touches a server-side API key —
each visitor pastes their own free Google AI Studio key, which is used only for
their own request and is never logged, written to disk, or stored beyond the
single pipeline run (same session-destruction guarantee as the FastAPI service,
see utils/session.py).

Originally built as a Gradio app targeting Hugging Face Spaces, but HF now requires
a PRO subscription for any Space with real compute (Gradio or Docker SDK) — only
static (no-backend) Spaces stay free. Rebuilt here for Streamlit Community Cloud
instead, the same free-hosting platform already proven for the Music Taste
Recommender project.

Run locally:
    streamlit run app/streamlit_app.py

Deploy: connect this repo to Streamlit Community Cloud (share.streamlit.io), set
this file as the entry point. No secrets need to be configured on the deployment
itself, since the key lives only in each visitor's own browser session.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from openai import APIError

from agents.orchestrator import OrchestratorAgent
from tests.test_pipeline import EMPLOYMENT_CONTRACT_CLAUSE, EVICTION_NOTICE, POLICE_SUMMONS
from utils.session import new_session

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
SEVERITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}
URGENCY_EMOJI = {"IMMEDIATE": "⏰", "SHORT_TERM": "🗓️", "GENERAL": "📌"}

EXAMPLES = {
    "Eviction notice": EVICTION_NOTICE,
    "Employment contract": EMPLOYMENT_CONTRACT_CLAUSE,
    "Police summons": POLICE_SUMMONS,
}


def render_report(result: dict) -> str:
    parts = [
        f"## {result['document_type']}",
        result["summary"],
    ]

    if result["your_rights"]:
        parts.append("### Your rights")
        parts += [f"- {r}" for r in result["your_rights"]]

    risks = sorted(result["risks"], key=lambda r: SEVERITY_ORDER.get(r.get("severity", "LOW"), 3))
    if risks:
        parts.append("### Risks")
        for r in risks:
            emoji = SEVERITY_EMOJI.get(r.get("severity", ""), "⚪")
            parts.append(f"**{emoji} {r.get('severity', '')}: {r.get('plain_explanation', '')}**")
            if r.get("what_document_says"):
                parts.append(f"- Document says: {r['what_document_says']}")
            if r.get("what_law_says"):
                parts.append(f"- Law says: {r['what_law_says']}")
            if r.get("legal_basis"):
                parts.append(f"- Legal basis: {r['legal_basis']}")

    if result["deadlines"]:
        parts.append("### Deadlines")
        for d in result["deadlines"]:
            emoji = URGENCY_EMOJI.get(d.get("urgency", ""), "•")
            parts.append(f"- {emoji} **{d.get('description', '')}** ({d.get('date_mentioned', '')})")

    if result["next_steps"]:
        parts.append("### Next steps")
        parts += [f"- {s}" for s in result["next_steps"]]

    if result["legal_referrals"]:
        parts.append("### Legal referrals")
        for ref in result["legal_referrals"]:
            line = f"- **{ref.get('name', '')}**"
            if ref.get("phone"):
                line += f" · {ref['phone']}"
            if ref.get("url"):
                line += f" · {ref['url']}"
            parts.append(line)

    parts.append(f"\n---\n*{result['disclaimer']}*")
    return "\n\n".join(parts)


st.set_page_config(page_title="Sheria Yangu", page_icon="⚖️", layout="centered")

st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
  html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

  .block-container { padding-top: 2rem; max-width: 760px; }

  /* Uganda flag colors (black / gold / red) used as a restrained accent palette
     rather than literally reproducing the flag. */
  :root {
    --ug-black: #1A1A1A;
    --ug-gold: #B8860B;
    --ug-red: #A6192E;
  }

  .hero { text-align: center; margin-bottom: 0.5rem; }

  .scale-svg { margin: 0 auto 0.5rem; display: block; }
  .scale-beam {
    transform-origin: 100px 30px;
    animation: scale-tilt 4.2s ease-in-out infinite alternate;
  }
  @keyframes scale-tilt {
    0%   { transform: rotate(-5deg); }
    100% { transform: rotate(5deg); }
  }

  .hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 800;
    font-size: 3.2rem;
    color: var(--ug-black);
    letter-spacing: -0.01em;
    margin: 0;
    line-height: 1.05;
  }
  .hero-subtitle {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--ug-gold);
    margin: 0.2rem 0 1rem;
  }

  .ug-divider {
    height: 5px;
    width: 180px;
    margin: 0.5rem auto 1.2rem;
    border-radius: 3px;
    background: linear-gradient(90deg,
      var(--ug-black) 0%, var(--ug-black) 33%,
      var(--ug-gold) 33%, var(--ug-gold) 66%,
      var(--ug-red) 66%, var(--ug-red) 100%);
  }

  .hero-intro {
    text-align: center;
    color: #4A4A4A;
    font-size: 1.02rem;
    max-width: 56ch;
    margin: 0 auto 1.8rem;
    line-height: 1.55;
  }

  .scope-box {
    background: #F3ECDC;
    border: 1px solid #E3D5B0;
    border-left: 4px solid var(--ug-gold);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1.6rem;
    font-size: 0.92rem;
    color: var(--ug-black);
  }
  .scope-box .scope-title {
    font-weight: 700;
    margin-bottom: 0.4rem;
  }
  .scope-box ul { margin: 0.3rem 0 0.7rem 1.1rem; padding: 0; }
  .scope-box li { margin-bottom: 0.15rem; }
  .disclaimer-line {
    border-left: 4px solid var(--ug-red);
    background: #FBEAEA;
    border-radius: 6px;
    padding: 0.7rem 1rem;
    margin-top: 0.6rem;
    font-size: 0.88rem;
    color: #5A1A1A;
  }
</style>

<div class="hero">
  <svg class="scale-svg" width="110" height="100" viewBox="0 0 200 160">
    <polygon points="70,150 130,150 105,130 95,130" fill="#1A1A1A"/>
    <rect x="97" y="30" width="6" height="100" fill="#1A1A1A"/>
    <circle cx="100" cy="30" r="6" fill="#B8860B"/>
    <g class="scale-beam">
      <line x1="30" y1="30" x2="170" y2="30" stroke="#1A1A1A" stroke-width="4"/>
      <line x1="30" y1="30" x2="30" y2="65" stroke="#1A1A1A" stroke-width="2"/>
      <path d="M10,65 Q30,90 50,65" fill="none" stroke="#B8860B" stroke-width="3"/>
      <line x1="170" y1="30" x2="170" y2="65" stroke="#1A1A1A" stroke-width="2"/>
      <path d="M150,65 Q170,90 190,65" fill="none" stroke="#B8860B" stroke-width="3"/>
    </g>
  </svg>
  <div class="hero-title">Sheria Yangu</div>
  <div class="hero-subtitle">Know Your Rights, Uganda 🇺🇬</div>
</div>

<div class="ug-divider"></div>

<div class="hero-intro">
  Paste a contract, notice, or summons and see what it says, what Ugandan law says,
  your rights, and your options, in plain language, in minutes.
</div>

<div class="scope-box">
  <div class="scope-title">Scope of this system</div>
  Covers eight common document types under Ugandan law: employment contracts, eviction
  notices, police summons, land and tenancy agreements, loan agreements, court orders,
  and government notices. It compares what your document says against what the named
  statute says. It does not review documents outside these categories, and it does not
  give strategic or tactical advice about what to do.
  <div class="disclaimer-line">
    ⚖️ <b>This is legal information, not legal advice.</b> The knowledge base and risk
    analysis have not been reviewed by a licensed advocate. For advice specific to your
    situation, consult a qualified advocate or contact the Uganda Law Society.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "Every analysis is a real AI request, so this demo runs on *your own* API key "
    "rather than a shared one. Get a free key at "
    "[aistudio.google.com/apikey](https://aistudio.google.com/apikey). "
    "It's used only for your request and is never logged or stored."
)

api_key = st.text_input("Your Google API key", type="password", placeholder="AIza...")

# A clicked example is applied here, before the text_area widget below is
# instantiated — session_state for a widget's key can only be set before that
# widget is created in a given run, not after (same pattern used in the Music
# Recommender demo's suggestion-click handling).
pending_example = st.session_state.pop("_pending_example", None)
if pending_example is not None:
    st.session_state.document_text_area = pending_example

st.caption("Or try a worked example:")
cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES.items(), strict=True):
    if col.button(label, use_container_width=True):
        st.session_state._pending_example = text
        st.rerun()

tab_text, tab_pdf = st.tabs(["Paste text", "Upload PDF"])
with tab_text:
    document_text = st.text_area(
        "Document text",
        height=250,
        key="document_text_area",
        placeholder="Paste a contract, notice, or summons here...",
    )
with tab_pdf:
    uploaded_file = st.file_uploader("Upload a PDF or .txt file", type=["pdf", "txt"])

submitted = st.button("Analyse document", type="primary")

if submitted:
    if not api_key.strip():
        st.warning(
            "Paste a free Google API key above first. Get one at "
            "[aistudio.google.com/apikey](https://aistudio.google.com/apikey)."
        )
    elif uploaded_file is None and not document_text.strip():
        st.warning("Paste some document text or upload a file first, or pick an example above.")
    else:
        session_id = new_session()
        orchestrator = OrchestratorAgent(session_id=session_id, api_key=api_key.strip())

        with st.spinner("Running the four-agent pipeline (this takes a moment)..."):
            try:
                if uploaded_file is not None:
                    raw_bytes = uploaded_file.read()
                    mime_type = "application/pdf" if uploaded_file.name.lower().endswith(".pdf") else "text/plain"
                    result = asyncio.run(orchestrator.run(raw_bytes=raw_bytes, mime_type=mime_type))
                else:
                    result = asyncio.run(orchestrator.run(document_text=document_text))
            except APIError:
                st.error(
                    "The AI provider rejected that request. Double-check the API key is valid and has quota remaining."
                )
                result = None
            except Exception as e:  # noqa: BLE001 - demo UI, show a clean message not a stack trace
                st.error(f"Something went wrong processing that document: {e}")
                result = None

        if result is not None:
            st.markdown(render_report(result))

st.markdown("---\nSource: [github.com/crisomara/sheria_yangu](https://github.com/crisomara/sheria_yangu)")

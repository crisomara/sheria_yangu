"""
Sheria Yangu — Gradio demo, bring-your-own-key.

Every /analyse call is a real LLM spend (unlike a typical ML demo with zero
per-request inference cost), so this demo never touches a server-side API key —
each visitor pastes their own free Google AI Studio key, which is used only for
their own request and is never logged, written to disk, or stored beyond the
single pipeline run (same session-destruction guarantee as the FastAPI service,
see utils/session.py).

Run locally:
    python demo/app.py

Deploy on Hugging Face Spaces: point the Space at this file as the entry point
(sdk: gradio); no secrets need to be configured on the Space itself, since the
key lives only in each visitor's own browser session.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import gradio as gr
from openai import APIError

from agents.orchestrator import OrchestratorAgent
from utils.session import new_session
from tests.test_pipeline import EVICTION_NOTICE, EMPLOYMENT_CONTRACT_CLAUSE, POLICE_SUMMONS

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
SEVERITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡"}
URGENCY_EMOJI = {"IMMEDIATE": "⏰", "SHORT_TERM": "🗓️", "GENERAL": "📌"}


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
            parts.append(f"**{emoji} {r.get('severity', '')} — {r.get('plain_explanation', '')}**")
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
            parts.append(f"- {emoji} **{d.get('description', '')}** — {d.get('date_mentioned', '')}")

    if result["next_steps"]:
        parts.append("### Next steps")
        parts += [f"- {s}" for s in result["next_steps"]]

    if result["legal_referrals"]:
        parts.append("### Legal referrals")
        for ref in result["legal_referrals"]:
            line = f"- **{ref.get('name', '')}**"
            if ref.get("phone"):
                line += f" — {ref['phone']}"
            if ref.get("url"):
                line += f" — {ref['url']}"
            parts.append(line)

    parts.append(f"\n---\n*{result['disclaimer']}*")
    return "\n\n".join(parts)


async def analyse(api_key: str, document_text: str) -> str:
    if not api_key or not api_key.strip():
        return (
            "⚠️ Paste a free Google API key above first — get one at "
            "[aistudio.google.com/apikey](https://aistudio.google.com/apikey). "
            "It's used only for this request and never stored."
        )
    if not document_text or not document_text.strip():
        return "⚠️ Paste some document text first, or pick one of the examples below."

    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id, api_key=api_key.strip())

    try:
        result = await orchestrator.run(document_text=document_text)
    except APIError:
        return (
            "⚠️ The AI provider rejected that request — double-check the API key is "
            "valid and has quota remaining."
        )
    except Exception as e:  # noqa: BLE001 - demo UI, show a clean message not a stack trace
        return f"⚠️ Something went wrong processing that document: {e}"

    return render_report(result)


with gr.Blocks(title="Sheria Yangu — Know Your Rights Uganda") as demo:
    gr.Markdown(
        "# 🇺🇬 Sheria Yangu — Know Your Rights\n"
        "Paste a contract, notice, or summons and see what it says, what Ugandan law "
        "says, your rights, and your options. **This is legal information, not legal "
        "advice.**\n\n"
        "Every analysis is a real AI request, so this demo runs on *your own* API key "
        "rather than a shared one — get a free key at "
        "[aistudio.google.com/apikey](https://aistudio.google.com/apikey), paste it "
        "below. It's used only for your request and is never logged or stored."
    )

    api_key_box = gr.Textbox(
        label="Your Google API key",
        type="password",
        placeholder="AIza...",
    )
    document_box = gr.Textbox(
        label="Document text",
        placeholder="Paste a contract, notice, or summons here...",
        lines=10,
    )
    submit_btn = gr.Button("Analyse document", variant="primary")
    output_box = gr.Markdown()

    gr.Examples(
        examples=[
            [EVICTION_NOTICE],
            [EMPLOYMENT_CONTRACT_CLAUSE],
            [POLICE_SUMMONS],
        ],
        inputs=[document_box],
        label="Or try a worked example",
    )

    submit_btn.click(fn=analyse, inputs=[api_key_box, document_box], outputs=output_box)

if __name__ == "__main__":
    demo.launch()

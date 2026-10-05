"""
Sheria Yangu — scored evaluation harness.

`tests/test_pipeline.py` runs the same three documents but only prints output for a
human to eyeball; nothing here was actually measured. This script turns that into real,
reportable numbers:

  1. Schema validity — did each agent stage return a dict with the fields the next
     stage / the API response model expects, across every run?
  2. Rubric checks — a small, hand-written set of "did the analysis at least surface
     the one obviously-relevant issue in this document" checks per sample document
     (e.g. the eviction notice's 3-day period vs. the statutory minimum). These are
     keyword/field-presence checks, not a legal-accuracy certification — the project's
     own README already states the knowledge base hasn't been reviewed by a licensed
     advocate, and this script doesn't change that; it's a regression signal, not a
     substitute for that review.
  3. Latency per full pipeline run (four sequential LLM calls).

Usage:
    python -m scripts.evaluate_pipeline
    # or, for a provider other than the one set in config.py:
    GOOGLE_API_KEY=... python -m scripts.evaluate_pipeline

Writes results to scripts/eval_results.json and prints a summary table.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from agents.orchestrator import OrchestratorAgent
from config import get_api_key
from tests.test_pipeline import EMPLOYMENT_CONTRACT_CLAUSE, EVICTION_NOTICE, POLICE_SUMMONS
from utils.session import new_session

EXPECTED_TOP_LEVEL_KEYS = {
    "session_id",
    "document_type",
    "summary",
    "your_rights",
    "risks",
    "deadlines",
    "next_steps",
    "legal_referrals",
    "disclaimer",
}

# Keyword-based rubric checks: for each document, at least one risk or deadline should
# mention something in the "any_of" list (case-insensitive substring match). These are
# intentionally loose — the goal is "did the pipeline notice the obviously relevant
# fact," not exact legal phrasing.
RUBRIC = {
    "Eviction Notice": {
        "text": EVICTION_NOTICE,
        "risks_any_of": ["notice", "3 day", "three day", "vacate"],
        "deadlines_any_of": ["3 day", "three day", "vacate"],
    },
    "Employment Contract Clause": {
        "text": EMPLOYMENT_CONTRACT_CLAUSE,
        "risks_any_of": ["notice", "5 day", "five day", "waiv", "unfair termination"],
        "deadlines_any_of": ["5 day", "five day", "notice"],
    },
    "Police Summons": {
        "text": POLICE_SUMMONS,
        "risks_any_of": ["lawyer", "legal representation", "counsel", "advocate"],
        "deadlines_any_of": ["5 july", "appear", "9:00"],
    },
}


def _matches_any(haystack_items: list[dict], fields: tuple[str, ...], needles: list[str]) -> bool:
    blob = " ".join(str(item.get(field, "")) for item in haystack_items for field in fields).lower()
    return any(n.lower() in blob for n in needles)


async def run_one(name: str, document_text: str, api_key: str) -> dict:
    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id, api_key=api_key)

    start = time.perf_counter()
    error = None
    result = None
    try:
        result = await orchestrator.run(document_text=document_text)
    except Exception as e:  # noqa: BLE001 - eval harness, want to record and continue
        error = f"{type(e).__name__}: {e}"
    latency_s = time.perf_counter() - start

    row = {
        "document": name,
        "latency_seconds": round(latency_s, 2),
        "error": error,
        "schema_valid": False,
        "risks_rubric_pass": False,
        "deadlines_rubric_pass": False,
        "n_risks": None,
        "n_deadlines": None,
    }

    if result is not None:
        row["schema_valid"] = EXPECTED_TOP_LEVEL_KEYS.issubset(result.keys())
        risks = result.get("risks", []) or []
        deadlines = result.get("deadlines", []) or []
        row["n_risks"] = len(risks)
        row["n_deadlines"] = len(deadlines)
        rubric = RUBRIC[name]
        row["risks_rubric_pass"] = _matches_any(
            risks,
            ("clause", "what_document_says", "what_law_says", "plain_explanation"),
            rubric["risks_any_of"],
        )
        row["deadlines_rubric_pass"] = _matches_any(
            deadlines,
            ("description", "date_mentioned"),
            rubric["deadlines_any_of"],
        )

    return row


async def main() -> None:
    api_key = get_api_key()
    rows = []
    for name, spec in RUBRIC.items():
        print(f"Running: {name}...")
        row = await run_one(name, spec["text"], api_key)
        rows.append(row)
        status = "OK" if row["error"] is None else f"ERROR: {row['error']}"
        print(
            f"  {status} — {row['latency_seconds']}s, "
            f"schema_valid={row['schema_valid']}, "
            f"risks_rubric={row['risks_rubric_pass']}, "
            f"deadlines_rubric={row['deadlines_rubric_pass']}"
        )

    n_ok = sum(1 for r in rows if r["error"] is None)
    n_schema_valid = sum(1 for r in rows if r["schema_valid"])
    n_risks_pass = sum(1 for r in rows if r["risks_rubric_pass"])
    n_deadlines_pass = sum(1 for r in rows if r["deadlines_rubric_pass"])
    avg_latency = sum(r["latency_seconds"] for r in rows) / len(rows)

    summary = {
        "n_documents": len(rows),
        "n_completed_without_error": n_ok,
        "schema_validity_rate": round(n_schema_valid / len(rows), 2),
        "risks_rubric_pass_rate": round(n_risks_pass / len(rows), 2),
        "deadlines_rubric_pass_rate": round(n_deadlines_pass / len(rows), 2),
        "avg_latency_seconds": round(avg_latency, 2),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")

    out_path = Path(__file__).parent / "eval_results.json"
    out_path.write_text(json.dumps({"summary": summary, "runs": rows}, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    asyncio.run(main())

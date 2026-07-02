"""
End-to-end pipeline test — Sheria Yangu Day 2

Three test scenarios:
  1. Eviction notice (unlawful — 3 days notice, no reason given)
  2. Employment contract (below statutory notice period)
  3. Police summons (citizen rights check)

Run with:
  cd sheria_yangu
  python -m tests.test_pipeline
"""

import asyncio
import json
import os
from utils.session import new_session
from agents.orchestrator import OrchestratorAgent

# ── Sample documents ──────────────────────────────────────────────────────────

EVICTION_NOTICE = """
NOTICE TO VACATE

To: Mr. John Okello
    Plot 14, Nakawa Division, Kampala

From: Mr. Robert Ssemakula (Landlord)

Date: 1 July 2026

You are hereby required to vacate the above premises within THREE (3) DAYS
from the date of this notice.

Failure to vacate will result in your belongings being removed from the
premises and the locks being changed.

No reason is given for this notice.

Signed: R. Ssemakula
"""

EMPLOYMENT_CONTRACT_CLAUSE = """
TERMINATION CLAUSE — Employment Contract

Employee: Ms. Grace Atim
Employer: Kampala Trading Company Ltd

Section 7 — Termination:
The employer may terminate this contract at any time by giving the employee
FIVE (5) DAYS written notice, or payment in lieu thereof, regardless of
the employee's length of service.

The employee waives any right to claim unfair termination provided the
employer pays the 5-day notice pay.

Section 8 — Annual Leave:
The employee is entitled to 10 working days of annual leave per year.
"""

POLICE_SUMMONS = """
UGANDA POLICE FORCE
CENTRAL POLICE STATION, KAMPALA

SUMMONS TO ATTEND

To: Ms. Sarah Namukasa
    Wandegeya, Kampala

You are hereby summoned to appear at Central Police Station, Kampala
on 5 July 2026 at 9:00 AM.

You are required to answer questions in connection with a matter under
investigation. Failure to appear may result in your arrest.

You are not required to bring a lawyer.

Officer: D/Cpl James Opolot
Badge No: 4471
"""

# ── Test runner ───────────────────────────────────────────────────────────────

async def run_test(name: str, document: str):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set. Add it to your .env file.")
        return

    session_id = new_session()
    orchestrator = OrchestratorAgent(session_id=session_id)

    try:
        result = await orchestrator.run(document_text=document)

        print(f"\nDocument type: {result['document_type']}")
        print(f"\nSUMMARY:\n{result['summary']}")

        print(f"\nYOUR RIGHTS ({len(result['your_rights'])}):")
        for r in result['your_rights']:
            print(f"  • {r}")

        print(f"\nRISKS ({len(result['risks'])}):")
        for risk in result['risks']:
            print(f"  [{risk['severity']}] {risk['plain_explanation']}")
            print(f"         Document says: {risk['what_document_says']}")
            print(f"         Law says:      {risk['what_law_says']}")
            print(f"         Legal basis:   {risk['legal_basis']}")

        print(f"\nDEADLINES ({len(result['deadlines'])}):")
        for d in result['deadlines']:
            print(f"  [{d['urgency']}] {d['description']} — {d['date_mentioned']}")

        print(f"\nNEXT STEPS ({len(result['next_steps'])}):")
        for step in result['next_steps']:
            print(f"  • {step}")

        print(f"\nDISCLAIMER:\n{result['disclaimer']}")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


async def main():
    print("Sheria Yangu — End-to-End Pipeline Test")
    print("Day 2: First real run\n")

    # Run all three test scenarios
    await run_test("Eviction Notice", EVICTION_NOTICE)
    await run_test("Employment Contract Clause", EMPLOYMENT_CONTRACT_CLAUSE)
    await run_test("Police Summons", POLICE_SUMMONS)

    print(f"\n{'='*60}")
    print("All tests complete.")


if __name__ == "__main__":
    asyncio.run(main())

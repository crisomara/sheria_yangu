# Sheria Yangu — Know Your Rights Uganda

> *Sheria* means "law" in Swahili. Every Ugandan citizen deserves to understand the documents that affect their life.

Sheria Yangu is an AI-powered multi-agent system that helps Ugandan citizens understand their legal documents in plain language. Upload or paste a contract, notice, or summons, and the system tells you what the document says, what Ugandan law says, what your rights are, and what options are available to you.

**Sheria Yangu provides legal information, not legal advice.** It surfaces what the law says versus what your document says. For advice specific to your situation, consult a qualified advocate.

---

## The Problem

Access to legal information in Uganda is a privilege. A citizen who receives an eviction notice, a police summons, or an employment contract they are pressured to sign immediately is at a significant disadvantage if they cannot afford an advocate. Sheria Yangu closes that gap — not by replacing advocates, but by ensuring every citizen walks into that conversation already knowing their rights.

---

## Architecture

```
User Input (text / PDF)
        │
        ▼
┌─────────────────────┐
│  Orchestrator Agent │  — Routes tasks, manages state, destroys session on completion
└─────────────────────┘
   │        │        │        │
   ▼        ▼        ▼        ▼
Intake  Research  Analysis  Synthesis
Agent    Agent     Agent     Agent
   │        │        │        │
   └────────┴────────┴────────┘
                │
                ▼
        Citizen Report
  ┌─────────────────────────┐
  │ What this document means│
  │ Your rights under law   │
  │ Risks (with severity)   │
  │ Deadlines to be aware of│
  │ Options available to you│
  │ Legal aid referrals     │
  └─────────────────────────┘
```

### Agent responsibilities

| Agent | Job |
|---|---|
| **Intake** | Classifies document type, extracts entities (parties, dates, amounts, obligations) |
| **Research** | Queries the Uganda statute knowledge base for relevant provisions |
| **Analysis** | Compares what the document says vs what the law says; flags risks and deadlines |
| **Synthesis** | Rewrites findings in plain language; surfaces rights and options |
| **Orchestrator** | Coordinates the pipeline; destroys session data after completion |

### Key concepts demonstrated (Kaggle course requirements)

- ✅ **Multi-agent system (ADK)** — Orchestrator + four specialist agents
- ✅ **MCP Server** — `mcp_tools/server.py` exposes the statute knowledge base as a tool, called via an in-process FastMCP client from the Research Agent
- ✅ **Security** — Session-scoped only; no PII or document content persists to disk

---

## Setup

```bash
git clone https://github.com/crisomara/sheria_yangu
cd sheria_yangu
pip install -r requirements.txt
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env (get one free at https://openrouter.ai/keys)
uvicorn main:app --reload
```

API is available at `http://localhost:8000`. Interactive docs at `/docs`.

---

## Usage

### Via the Kaggle notebook (recommended for demo)

Open `notebooks/sheria_yangu_demo.ipynb` and run all cells.
Three worked examples are provided: eviction notice, employment contract, police summons.

### Via the API

```bash
curl -X POST http://localhost:8000/analyse/text \
  -H "Content-Type: application/json" \
  -d '{"text": "You are hereby required to vacate the premises within 3 days..."}'
```

---

## Document types supported

- Employment Contract / Termination Notice
- Eviction Notice / Notice to Vacate
- Police Summons
- Land Agreement
- Tenancy Agreement
- Loan Agreement
- Court Order
- Government Notice

---

## Legal knowledge base

Provisions drawn from:
- Constitution of Uganda 1995 (as amended)
- Employment Act 2006 (Cap. 219)
- Landlord and Tenant Act 2022
- Land Act 1998 (Cap. 227)
- Police Act 2006 (Cap. 303)
- Contracts Act 2010
- Tier 4 Microfinance Institutions and Moneylenders Act 2016

---

## Legal referrals

Sheria Yangu always includes referral information in every report:

| Organisation | Contact |
|---|---|
| Uganda Law Society | 0414-254848 |
| FIDA Uganda (free legal aid for women) | 0414-530848 |
| LASPNET | laspnet.org |
| Uganda Human Rights Commission (toll-free) | 0800-200-500 |

---

## Security & privacy

- No document content is written to disk at any point
- Sessions are in-memory only, expire after 10 minutes, and are explicitly destroyed after each pipeline run
- No user data is logged or retained between requests
- The API accepts text and PDF only; no executable file types are permitted

---

## Disclaimer

Sheria Yangu provides legal information based on Ugandan law, not legal advice. For advice specific to your situation, consult a qualified advocate or contact the Uganda Law Society.

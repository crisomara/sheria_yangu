# Sheria Yangu — Know Your Rights Uganda

**Track:** Agents for Good
**Tagline:** A multi-agent AI system that tells Ugandan citizens what their legal documents actually mean — in plain language.

---

## The Problem

Access to legal information in Uganda is a privilege.

When a tenant receives an eviction notice, an employee is handed a contract to sign on the spot, or a citizen receives a police summons — they are at a significant disadvantage if they cannot afford an advocate. Legal aid organisations exist but are stretched thin. The Uganda Law Society estimates that fewer than 1 in 10 Ugandans who need legal assistance actually receive it.

The result: people sign contracts that violate their statutory rights, vacate homes based on unlawful notices, and attend police interviews without knowing they are entitled to have a lawyer present.

Sheria Yangu addresses this gap directly. Not by replacing advocates — but by ensuring every citizen walks into that conversation already knowing their rights.

---

## Why Agents?

This problem is not a single-step lookup. Understanding a legal document requires:

1. **Classification** — what kind of document is this?
2. **Research** — what Ugandan law applies?
3. **Reasoning** — where does the document diverge from what the law requires?
4. **Communication** — how do you explain this to someone with no legal training?

Each step requires different capabilities and different prompting strategies. A single LLM call cannot reliably do all four well. A multi-agent architecture where each agent is purpose-built for its specific task produces dramatically better results — and makes the system auditable step by step.

---

## Architecture

```
User Input (text / PDF)
        |
        v
┌─────────────────────┐
│  Orchestrator Agent │  Routes tasks, manages state, destroys session
└─────────────────────┘
   |        |        |        |
   v        v        v        v
Intake  Research  Analysis  Synthesis
Agent    Agent     Agent     Agent
   |        |        |        |
   +--------+--------+--------+
                |
                v
        Structured Report
  ┌─────────────────────────────┐
  │ What this document means    │
  │ Your rights under Ugandan   │
  │ law (with citations)        │
  │ Risks flagged by severity   │
  │ Deadlines to be aware of    │
  │ Options available to you    │
  │ Legal aid referrals         │
  └─────────────────────────────┘
```

### Agent responsibilities

| Agent | Model | Job |
|---|---|---|
| Intake | Gemini 2.5 Flash | Classifies document type, extracts entities |
| Research | Gemini 2.5 Flash | Queries MCP statute knowledge base |
| Analysis | Antigravity | Deep legal reasoning: document vs law |
| Synthesis | Gemini 2.5 Flash | Plain-language citizen report |
| Orchestrator | — | Coordinates pipeline, manages sessions |

### Why Antigravity for Analysis?

The Analysis Agent performs the most cognitively demanding task: comparing every clause in a document against Ugandan statutory provisions and identifying gaps. This requires multi-step reasoning that benefits from Antigravity's extended thinking capability. Routine agents (Intake, Research, Synthesis) use standard Gemini 2.5 Flash.

---

## Key Concepts Demonstrated

### 1. Multi-Agent System (ADK pattern)
Five agents with explicit roles, structured input/output contracts, and an orchestrator that manages state and sequencing. Each agent is independently testable.

### 2. Custom MCP Server
`mcp_tools/server.py` exposes the Uganda statute knowledge base as three registered tools, called by the Research Agent through an in-process FastMCP client:
- `lookup_statutes(document_type, context)` — finds relevant provisions
- `list_acts()` — lists all Acts in the knowledge base
- `get_section(act_name, section)` — retrieves a specific section

### 3. Antigravity
The Analysis Agent uses Google's Antigravity reasoning model for the legal comparison step — the most complex reasoning task in the pipeline.

### 4. Security
- Sessions are UUID-keyed, in-memory only
- No document content is written to disk at any point
- Sessions expire after 10 minutes and are explicitly destroyed after each pipeline run
- No user data persists between requests

---

## The Legal Information vs Legal Advice Distinction

Every agent in the pipeline is explicitly constrained to surface **legal information** — what the law says — rather than **legal advice** — what the citizen should do.

This distinction is:
- **Legally required** — providing legal advice without a licence violates Uganda's Advocates Act Cap 267
- **Ethically important** — an AI system should not substitute for professional legal judgment
- **Architecturally enforced** — the synthesis agent's system prompt explicitly prohibits directive language

Every report ends with referrals to the Uganda Law Society, FIDA Uganda, LASPNET, and the Uganda Human Rights Commission.

---

## Legal Knowledge Base

Provisions drawn from official Uganda Law Reform Commission publications:

| Act | Provisions covered |
|---|---|
| Constitution of Uganda 1995 | Articles 23, 24, 26, 28 |
| Employment Act 2006 | Sections 41, 52, 58, 64, 83 |
| Landlord and Tenant Act 2022 | Sections 19, 30, 47 |
| Land Act 1998 | Sections 3, 59 |
| Police Act 2006 | Sections 24, 25 |
| Contracts Act 2010 | Sections 12, 45 |
| Tier 4 Microfinance Act 2016 | Section 78 |

---

## Document Types Supported

- Employment Contract / Termination Notice
- Eviction Notice / Notice to Vacate
- Police Summons
- Land Agreement
- Tenancy Agreement
- Loan Agreement
- Court Order
- Government Notice

---

## Impact

Uganda has a population of approximately 48 million people. The majority live outside urban centres with limited access to legal services. Sheria Yangu is designed for:

- Low-literacy adaptation (plain language output)
- Low-bandwidth environments (text-only, no images required)
- Mobile-first delivery (API-first architecture, easily wrapped in SMS or WhatsApp)

The system is not a replacement for advocates. It is the layer that ensures citizens are informed before they need one.

---

## Setup

```bash
git clone https://github.com/crisomara/sheria_yangu
cd sheria_yangu
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY to .env (free at https://aistudio.google.com/apikey)
python -m tests.test_pipeline
```

---

*Sheria Yangu provides legal information based on Ugandan law, not legal advice.*
*For advice specific to your situation, contact the Uganda Law Society: 0414-254848*

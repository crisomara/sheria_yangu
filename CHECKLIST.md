# Portfolio Project Checklist — Sheria Yangu

Every project must check every box before it counts as "portfolio-ready" and before
work moves on to the next project. Derived directly from the ML-portfolio hiring
guidelines pasted 2026-08-21 (full source discussion in
`Desktop/PORTFOLIO-PROJECT-PLANS/portfolio_rubric_and_roadmap.md`).

Updated 2026-08-22 during the deployment/demo/Docker retrofit — full context in
`Desktop/PORTFOLIO-PROJECT-PLANS/plan_sheria_yangu_retrofit.md`. Checked only where
actually verified, not aspirationally.

## 1. End-to-End Implementation
- [ ] Data preprocessing pipeline present and documented — N/A in the classic ML sense: this is an LLM-orchestration project (pretrained models via API, no training data pipeline). Closest analogue is the Intake Agent's entity extraction, documented below.
- [x] Feature engineering step present and documented — Intake Agent's structured entity extraction (parties, dates, amounts, obligations) from raw document text, documented in README's Architecture section
- [ ] Training pipeline present — genuinely N/A, no model training happens (pretrained LLMs via API only); not force-checked
- [x] Evaluation step present, with real metrics — `scripts/evaluate_pipeline.py` (schema validity rate, rubric pass rate, latency) — **run it yourself and paste real numbers into the README's Results section**, I couldn't run it myself without a Google API key, see note below
- [x] Deployed: runs somewhere beyond a notebook — FastAPI (`main.py`) verified: local run + Docker build + Docker run, `/health` and `/docs` both responding for real; Gradio demo (`demo/app.py`) verified booting locally with working guard-rail paths
- [x] Monitoring present, or at minimum a stated monitoring plan — README "Monitoring" section

## 2. Reproducibility
- [x] Clean, structured codebase (not notebooks-only)
- [x] `requirements.txt` included
- [x] A stranger can clone and run it without DMing the author — self-service: free Google API key, documented setup, verified `uvicorn main:app` boots and `/health` responds with nothing beyond `pip install`

## 3. Business Relevance
- [x] Tied to a practical/business outcome, not just a metric — README "Business relevance" section (access-to-justice framing)
- [x] That outcome framing is stated explicitly in the README

## 4. Scalability Awareness
- [x] Latency, cost, and infrastructure constraints are discussed — README "Scalability considerations" (per-request LLM cost, sequential agent dependency chain, statute-lookup caching opportunity, rate limiting)
- [x] A stated plan for how it would scale beyond the demo

## 5. Documentation & Storytelling
- [x] README has a problem statement
- [x] README has an architecture diagram — Mermaid diagram (replaced the previous ASCII block), renders natively on GitHub
- [ ] README has results — section exists and explains what's measured, but needs real numbers pasted in from an actual `scripts/evaluate_pipeline.py` run (couldn't run it myself — needs a real Google API key, which I don't have and shouldn't ask for)
- [x] README has "how to run" instructions — covers API, Gradio demo, Kaggle notebook, and Docker
- [ ] (Bonus) a blog post or demo video — not done, optional

## 6. Modern Stack
- [x] Docker — built and run-tested: `docker build` succeeded, `docker run` served real `/health` responses on a fresh container
- [ ] Experiment tracking (e.g. MLflow) — genuinely doesn't map onto an LLM-orchestration project (no training runs to track); `scripts/eval_results.json` is the closest analogue but isn't MLflow-equivalent tracking over time. Left unchecked rather than force-fit.
- [x] Other tools where relevant — MCP server (`mcp_tools/server.py`) exposing the statute knowledge base as a tool

## 7. Recruiter-Scan Signals
- [x] README is understandable in 30 seconds
- [x] Commit history reads as polished work — pre-existing, PR-based history already reads well
- [ ] Live deployment link (Streamlit / Gradio / Hugging Face Spaces) — Gradio app built and verified locally, but not yet deployed to Hugging Face Spaces (needs the user's own HF account — same one-click pattern as Music Recommender's Streamlit Cloud link)
- [x] Architecture diagram a non-technical reviewer can follow — Mermaid diagram

## 8. Elevation Pass
- [x] Data augmentation/preprocessing pipeline — Intake Agent's entity extraction (see item 1)
- [ ] MLOps practices: model versioning, experiment tracking — N/A, no models are trained/versioned here; not force-checked (same reasoning as item 6)
- [x] Deployed as a REST API (Flask/FastAPI) — FastAPI, verified with real `/health` + `/docs` responses, both locally and via Docker
- [x] Demo app (Streamlit/Gradio) — Gradio, verified booting locally with working guard-rails; live HF Spaces link pending (see item 7)
- [x] Written explanation of a real-world application of the system — README "Business relevance"

## 9. Forward-Looking Signals (2025+)
- [x] Any LLM use is responsible and cost-aware, stated as such — close to the project's core design already: rate limiting, fallback models on quota errors, and (new) a bring-your-own-key demo specifically so the public demo never touches the author's own API quota/cost
- [x] Bias/explainability/compliance trade-offs considered and stated where relevant — the "legal information, not legal advice" framing, the disclaimer, and the explicit "knowledge base not reviewed by a licensed advocate, treat as prototype" statement
- [ ] Multimodal awareness noted where relevant — PDF upload exists but is text extraction only, not true multimodal (vision/document) understanding; not claiming more than what's actually built
- [x] Project is treated as living — this retrofit itself is evidence, on top of an already-active PR-based commit history

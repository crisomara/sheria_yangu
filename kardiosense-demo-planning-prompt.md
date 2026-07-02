# Prompt: KardioSense Landing Page Audit + AI Demo Planning

> Paste this into an agentic coding LLM (e.g. Claude Code) with access to the
> `crisomara/kardiosense` repo. It's built as three sequential tasks so the
> model works through them in order and gives you decisions, not just options.

---

## Context (paste as-is)

You're advising KardioSense, an AI-powered cardiac diagnostics startup built
by a small team (CEO/lead engineer, technical co-founder, clinical co-founder).

**Current stack:**
- Landing page: React + TypeScript + Vite, deployed on Vercel, repo at
  `github.com/crisomara/kardiosense`
- Backend: FastAPI + Supabase (Postgres + auth), JWT middleware, facility-scoped
  access policies
- Model: dual-branch fusion architecture — ResNet-1D + BiLSTM + MultiHead
  Attention + AttentionPool with lead-agnostic masking (signal branch) fused
  with an XGBoost clinical risk branch. 5-class multilabel output: NORM, MI,
  AFIB, STTC, CD.
- Deployment target: TFLite FP32 on Raspberry Pi 4 for prototyping (INT8
  blocked by an onnx2tf BiLSTM bug); STM32H743 is the production hardware
  target.
- Acquisition hardware: TI ADS1294 front-end + nRF52840 BLE, with a Flutter
  app for signal capture.
- Recent benchmark headline: ~5x robustness advantage over ISIBrno at 1-lead
  configurations for MI detection on PTB-XL, with CODE-15% external
  validation in progress.

Your job is to work through three tasks below **in order**, and not skip
ahead. Each task ends with a required deliverable format — follow it exactly.

---

## Task 1 — Landing Page Repo Audit

Clone/open the repo and produce a **prioritized punch list** of what needs
attention before the site is demo/investor-ready. Check specifically for:

- Broken links, dead routes, console errors
- Build/deploy health (Vercel build warnings, env var gaps)
- Content gaps or placeholder text ("Lorem ipsum", TODO comments, stale copy)
- Brand/tone consistency (should read as Commonwealth English, clinical but
  accessible)
- Responsiveness / mobile layout issues
- Image optimization and load performance
- SEO basics (meta tags, alt text, sitemap)
- Any half-finished features visible in the codebase but not on the live site

**Deliverable format:**
A table with columns: `Priority (Critical/High/Medium/Low) | Issue | File/Path | Suggested Fix`.
Keep it to the top 15–20 items — don't pad it.

---

## Task 2 — AI KardioSense Demo Planning

Design a demo of a **clinician-facing dashboard** with three functional
pieces:

1. **Patient details input** — clinician manually enters patient
   demographics/history/context
2. **Signal ingestion** — receives ECG signal from hardware (ADS1294 +
   nRF52840 BLE, or a simulated/replayed signal as fallback)
3. **Signal visualization** — live or replayed ECG waveform rendering
4. **Prediction/diagnosis output** — model output across the 5 classes, with
   confidence, and a clear statement of which leads were used (tying into the
   1-lead robustness result)

For each piece, specify:
- What's reusable from the existing stack (FastAPI backend, Supabase, model
  inference pipeline, Flutter capture app) vs. what needs to be newly built
  for the dashboard itself
- Data flow from hardware → backend → dashboard → model → back to dashboard
- Rough component/file list if it were built in the existing React/TS/Vite
  frontend (or state clearly if it needs a separate app)
- A day-by-day build plan given a short, fixed build window (state your
  assumed window if not given one, e.g. 5–7 days)

**Deliverable format:**
1. A short architecture description (prose + a simple text/ASCII diagram of
   the data flow)
2. A table: `Component | Reuse or New Build | Owner-ready effort estimate`
3. A day-by-day build plan

---

## Task 3 — Take a Stand

Do not present this as a menu of options. For each decision below, **pick
one, state it as a recommendation, and give a 1–2 sentence rationale.**
Flag anywhere you're genuinely uncertain, but default to a decision rather
than "it depends."

- **Live hardware vs. simulated/replayed signal for the demo.** Which do you
  run live, and what's the fallback if hardware fails mid-demo?
- **Which lead configuration to showcase.** Full 12-lead, or lean into the
  1-lead robustness result as the headline?
- **Scope cut line.** Given the build window, what's explicitly OUT of scope
  for this demo (e.g. multi-patient history, auth/login, PDF export)?
- **How the output is framed.** "Diagnosis" vs. "diagnostic aid" / decision
  support — this has regulatory and liability implications, so pick the
  framing and say why.
- **Who the demo is for.** Investor pitch, clinical partner validation, or
  competition judges (if for the Kaggle-style capstone context) — the answer
  changes what "impressive" means, so name the audience and let it drive the
  above choices.

**Deliverable format:**
A short numbered list, one recommendation per line, bolded decision + one-line
rationale. No hedging, no "you could also consider."

---

## Final output

Combine all three tasks into one markdown document with headers matching the
task titles above, so it can be dropped straight into planning notes.

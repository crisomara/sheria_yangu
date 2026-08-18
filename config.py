"""
Sheria Yangu — Central Configuration

API SETUP:
  Development/Demo: Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env
  Production:       Set GOOGLE_API_KEY in .env (unlocks Antigravity)

Provider priority (when USE_GOOGLE_API is False): OPENAI_API_KEY, then OPENROUTER_API_KEY.

To switch to Google API (Antigravity):
  1. Add billing to your Google Cloud project
  2. Set GOOGLE_API_KEY in .env
  3. Set USE_GOOGLE_API = True below
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API provider switch ───────────────────────────────────────────────────────
# Set to True when Google API key with billing is available
# This unlocks the real Antigravity model for the Analysis Agent
USE_GOOGLE_API = False

# ── API keys ──────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# ── Active key (used by all agents) ──────────────────────────────────────────
def get_api_key() -> str:
    if USE_GOOGLE_API:
        if not GOOGLE_API_KEY:
            raise ValueError("USE_GOOGLE_API is True but GOOGLE_API_KEY is not set.")
        return GOOGLE_API_KEY
    elif OPENAI_API_KEY:
        return OPENAI_API_KEY
    elif OPENROUTER_API_KEY:
        return OPENROUTER_API_KEY
    else:
        raise ValueError(
            "No API key set. Add OPENAI_API_KEY or OPENROUTER_API_KEY to your .env file."
        )

# ── Model configuration ───────────────────────────────────────────────────────
# OpenRouter models
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_STANDARD_MODEL = "google/gemini-2.5-flash"   # for intake, research, synthesis
OPENROUTER_REASONING_MODEL = "google/gemini-2.5-flash"  # for analysis (swap when credits available)
OPENROUTER_FALLBACK_MODEL  = "meta-llama/llama-3.3-70b-instruct:free"

# Direct OpenAI models
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_STANDARD_MODEL  = "gpt-4o-mini"  # for intake, research, synthesis
OPENAI_REASONING_MODEL = "gpt-4o"       # for analysis
OPENAI_FALLBACK_MODEL  = "gpt-4o-mini"

# Google API models (production — swap USE_GOOGLE_API to True)
GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GOOGLE_STANDARD_MODEL  = "gemini-2.0-flash"           # intake, research, synthesis
GOOGLE_REASONING_MODEL = "models/antigravity-preview-05-2026"  # analysis — deep legal reasoning

# ── Active model selection ────────────────────────────────────────────────────
def get_base_url() -> str:
    if USE_GOOGLE_API:
        return GOOGLE_BASE_URL
    return OPENAI_BASE_URL if OPENAI_API_KEY else OPENROUTER_BASE_URL

def get_standard_model() -> str:
    if USE_GOOGLE_API:
        return GOOGLE_STANDARD_MODEL
    return OPENAI_STANDARD_MODEL if OPENAI_API_KEY else OPENROUTER_STANDARD_MODEL

def get_reasoning_model() -> str:
    """
    Returns the reasoning model for the Analysis Agent.
    Production: Google Antigravity (models/antigravity-preview-05-2026)
    Demo:       gpt-4o (direct OpenAI) or gemini-2.5-flash (OpenRouter), whichever key is set
    """
    if USE_GOOGLE_API:
        return GOOGLE_REASONING_MODEL
    return OPENAI_REASONING_MODEL if OPENAI_API_KEY else OPENROUTER_REASONING_MODEL

def get_fallback_model() -> str:
    return OPENAI_FALLBACK_MODEL if OPENAI_API_KEY else OPENROUTER_FALLBACK_MODEL

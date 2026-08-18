"""
Sheria Yangu — Central Configuration

API SETUP (default provider is Google):
  Default:   Set GOOGLE_API_KEY in .env (a free Google AI Studio key works for
             the standard tier; the reasoning tier needs a billed Google
             Cloud project and otherwise falls back automatically).
  Alternate: Set USE_GOOGLE_API = False below, then set OPENAI_API_KEY or
             OPENROUTER_API_KEY in .env (provider priority: OpenAI, then
             OpenRouter).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API provider switch ───────────────────────────────────────────────────────
# Default provider is Google. Set to False to use OpenAI/OpenRouter instead.
USE_GOOGLE_API = True

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
GOOGLE_STANDARD_MODEL  = "gemini-3.6-flash"   # intake, research, synthesis
GOOGLE_REASONING_MODEL = "gemini-3.1-pro-preview"  # analysis — deep legal reasoning
GOOGLE_FALLBACK_MODEL  = "gemini-3.6-flash"

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
    Default:   gemini-3.1-pro-preview (deep-reasoning tier; "Antigravity" in project
               docs). Requires a billed Google Cloud project; falls back to
               gemini-3.6-flash on 402/429 if billing isn't enabled.
    Alternate: gpt-4o (direct OpenAI) or gemini-2.5-flash (OpenRouter), whichever key is set
    """
    if USE_GOOGLE_API:
        return GOOGLE_REASONING_MODEL
    return OPENAI_REASONING_MODEL if OPENAI_API_KEY else OPENROUTER_REASONING_MODEL

def get_fallback_model() -> str:
    if USE_GOOGLE_API:
        return GOOGLE_FALLBACK_MODEL
    return OPENAI_FALLBACK_MODEL if OPENAI_API_KEY else OPENROUTER_FALLBACK_MODEL

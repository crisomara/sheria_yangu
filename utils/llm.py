"""
Shared LLM call helper - Sheria Yangu

Wraps client.chat.completions.create with automatic fallback to a secondary
model on payment-required (402) or rate-limit/quota (429) errors, so a quota
hit on any agent degrades to the fallback model instead of crashing that
pipeline run.
"""

from openai import APIStatusError


async def create_with_fallback(client, primary_model: str, fallback_model: str, messages: list[dict], agent_label: str):
    try:
        return client.chat.completions.create(model=primary_model, messages=messages)
    except APIStatusError as e:
        if e.status_code in (402, 429):
            print(f"[{agent_label}] {primary_model} unavailable ({e.status_code}), falling back to {fallback_model}...")
            return client.chat.completions.create(model=fallback_model, messages=messages)
        raise

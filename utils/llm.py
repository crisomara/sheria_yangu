"""
Shared LLM call helpers - Sheria Yangu

create_with_fallback wraps client.chat.completions.create with automatic
fallback to a secondary model on payment-required (402) or rate-limit/quota
(429) errors, so a quota hit on any agent degrades to the fallback model
instead of crashing that pipeline run.

parse_agent_json turns a model reply into a checked dict. Every agent uses it,
so an empty reply, broken JSON or a reply in the wrong shape is reported the
same way (ModelOutputError) instead of surfacing later as a server error.
"""

import json
import re

from openai import APIStatusError
from pydantic import BaseModel, ValidationError

from utils.errors import ModelOutputError


async def create_with_fallback(client, primary_model: str, fallback_model: str, messages: list[dict], agent_label: str):
    try:
        return client.chat.completions.create(model=primary_model, messages=messages)
    except APIStatusError as e:
        if e.status_code in (402, 429):
            print(f"[{agent_label}] {primary_model} unavailable ({e.status_code}), falling back to {fallback_model}...")
            return client.chat.completions.create(model=fallback_model, messages=messages)
        raise


def parse_agent_json(response, schema: type[BaseModel], agent_label: str) -> dict:
    """
    Reads the JSON in a chat completion and checks it against `schema`.

    Returns the validated data as a plain dict. Raises ModelOutputError when
    the reply is missing, is not JSON, or does not match the schema. The error
    message names the fields at fault and never quotes the reply itself, so
    no document content can leak through it.
    """
    try:
        raw = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as e:
        raise ModelOutputError(f"{agent_label}: the model returned no message.") from e
    if not isinstance(raw, str) or not raw.strip():
        raise ModelOutputError(f"{agent_label}: the model returned an empty reply.")

    cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ModelOutputError(f"{agent_label}: the model reply was not valid JSON.") from e

    try:
        return schema.model_validate(data).model_dump()
    except ValidationError as e:
        fields = ", ".join(sorted({".".join(str(part) for part in error["loc"]) or "reply" for error in e.errors()}))
        raise ModelOutputError(f"{agent_label}: the model reply did not have the expected shape ({fields}).") from e

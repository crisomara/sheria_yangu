"""
Session management for Sheria Yangu.

SECURITY DESIGN:
- Sessions are UUID-keyed in-memory dicts only.
- No session data is written to disk or any database.
- Sessions expire after SESSION_TTL_SECONDS.
- The user document is processed and discarded within a single pipeline run.
"""

import uuid
import time
from typing import Optional

SESSION_TTL_SECONDS = 600

_sessions: dict[str, dict] = {}


def new_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"created_at": time.time(), "data": {}}
    _evict_expired()
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    _evict_expired()
    session = _sessions.get(session_id)
    if session is None:
        return None
    if time.time() - session["created_at"] > SESSION_TTL_SECONDS:
        del _sessions[session_id]
        return None
    return session["data"]


def update_session(session_id: str, key: str, value) -> None:
    session = _sessions.get(session_id)
    if session:
        session["data"][key] = value


def destroy_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def _evict_expired() -> None:
    now = time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s["created_at"] > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]

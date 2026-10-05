"""Unit tests for the in-memory session store (utils/session.py)."""

import uuid

from utils import session


def test_new_session_returns_uuid_and_empty_data():
    sid = session.new_session()
    assert uuid.UUID(sid)
    assert session.get_session(sid) == {}
    session.destroy_session(sid)


def test_update_and_get_session():
    sid = session.new_session()
    session.update_session(sid, "intake", {"document_type": "Eviction Notice"})
    assert session.get_session(sid) == {"intake": {"document_type": "Eviction Notice"}}
    session.destroy_session(sid)


def test_update_unknown_session_is_a_noop():
    session.update_session("does-not-exist", "k", "v")
    assert session.get_session("does-not-exist") is None


def test_destroy_session_removes_data():
    sid = session.new_session()
    session.destroy_session(sid)
    assert session.get_session(sid) is None
    # Destroying twice must not raise.
    session.destroy_session(sid)


def test_expired_session_is_evicted(monkeypatch):
    now = [1_000_000.0]
    monkeypatch.setattr(session.time, "time", lambda: now[0])
    sid = session.new_session()
    assert session.get_session(sid) == {}

    now[0] += session.SESSION_TTL_SECONDS + 1
    assert session.get_session(sid) is None
    assert sid not in session._sessions

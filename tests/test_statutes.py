"""Unit tests for the statute knowledge base and the MCP tool functions."""

import pytest

from knowledge.uganda_statutes import STATUTE_DB
from mcp_tools import server


def _fn(tool):
    # FastMCP's @mcp.tool() may wrap the function in a Tool object; the original
    # callable is kept on `.fn`.
    return getattr(tool, "fn", tool)


lookup_statutes = _fn(server.lookup_statutes)
list_acts = _fn(server.list_acts)
get_section = _fn(server.get_section)


def test_statute_db_entries_are_well_formed():
    assert STATUTE_DB, "knowledge base must not be empty"
    for statute in STATUTE_DB:
        for key in ("act", "section", "title", "text", "tags"):
            assert key in statute, f"{statute.get('section')} is missing {key}"
        assert statute["text"].strip()
        assert isinstance(statute["tags"], list) and statute["tags"]


@pytest.mark.parametrize(
    "document_type, expected_tag",
    [
        ("Employment Contract", "employment"),
        ("Eviction Notice", "tenancy"),
        ("Police Summons", "police"),
        ("Land Agreement", "land"),
    ],
)
def test_lookup_returns_relevant_statutes(document_type, expected_tag):
    results = lookup_statutes(document_type)
    assert 0 < len(results) <= 10
    assert any(expected_tag in s["tags"] for s in results)


def test_lookup_unknown_type_falls_back_to_constitutional_rights():
    results = lookup_statutes("Something Unrecognised")
    assert results
    assert all({"rights", "constitutional"} & set(s["tags"]) for s in results)


def test_lookup_context_widens_search():
    results = lookup_statutes("Other", context="my employer wants to dismiss me")
    assert any("employment" in s["tags"] for s in results)


def test_list_acts_is_sorted_and_unique():
    acts = list_acts()
    assert acts == sorted(set(acts))
    assert "Constitution of Uganda 1995" in acts


def test_get_section_found_and_missing():
    first = STATUTE_DB[0]
    assert get_section(first["act"], first["section"]) == first
    assert get_section("No Such Act", "Section 0") is None

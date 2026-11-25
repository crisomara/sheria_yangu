"""Unit tests for the statute knowledge base and the MCP tool functions."""

import asyncio

import pytest
from fastmcp import Client

from knowledge.uganda_statutes import STATUTE_DB
from mcp_tools import server


def _fn(tool):
    # FastMCP's @mcp.tool() may wrap the function in a Tool object; the original
    # callable is kept on `.fn`.
    return getattr(tool, "fn", tool)


lookup_statutes = _fn(server.lookup_statutes)
list_acts = _fn(server.list_acts)
get_section = _fn(server.get_section)

DOCUMENT_TYPES = [
    "Employment Contract",
    "Eviction Notice",
    "Tenancy Agreement",
    "Police Summons",
    "Land Agreement",
    "Loan Agreement",
    "Court Order",
    "Government Notice",
]


def _sections(results, act_part):
    return [s["section"] for s in results if act_part in s["act"]]


def _is_constitutional(statute):
    return "constitutional" in statute["tags"]


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
        ("Eviction Notice", "landlord"),
        ("Police Summons", "police"),
        ("Land Agreement", "land"),
    ],
)
def test_lookup_returns_relevant_statutes(document_type, expected_tag):
    results = lookup_statutes(document_type)
    assert 0 < len(results) <= server.MAX_RESULTS
    assert any(expected_tag in s["tags"] for s in results)


# The sections each kind of document turns on. Before results were ranked, the
# lookup kept the first ten matches in file order and every one of these was cut.
@pytest.mark.parametrize(
    "document_type, act_part, sections",
    [
        ("Employment Contract", "Employment Act", {"Section 58", "Section 65", "Section 69", "Section 41"}),
        ("Eviction Notice", "Landlord and Tenant Act", {"Section 45", "Section 38"}),
        ("Eviction Notice", "Land (Amendment) Act", {"Section 2 (Inserting Section 32A)", "Section 5"}),
        ("Tenancy Agreement", "Landlord and Tenant Act", {"Section 3", "Section 4", "Section 30", "Section 38"}),
        (
            "Police Summons",
            "Police (Amendment) Act",
            {
                "Section 18 (Inserting Section 27A)",
                "Section 18 (Inserting Section 27A, sub 3)",
                "Section 15",
            },
        ),
        ("Loan Agreement", "Tier 4 Microfinance", {"Section 78"}),
        ("Land Agreement", "Land (Amendment) Act", {"Section 2 (Inserting Section 32A)", "Section 3"}),
    ],
)
def test_lookup_returns_the_governing_sections(document_type, act_part, sections):
    found = set(_sections(lookup_statutes(document_type), act_part))
    assert sections <= found, f"missing {sorted(sections - found)}"


@pytest.mark.parametrize(
    "document_type, first_section",
    [
        ("Employment Contract", "Section 58"),
        ("Eviction Notice", "Section 45"),
        ("Police Summons", "Section 18 (Inserting Section 27A)"),
    ],
)
def test_most_relevant_section_comes_first(document_type, first_section):
    assert lookup_statutes(document_type)[0]["section"] == first_section


@pytest.mark.parametrize(
    "document_type, foreign_act",
    [
        # "termination" and "notice" are tags in both Acts. They must not cross over.
        ("Eviction Notice", "Employment Act"),
        ("Tenancy Agreement", "Employment Act"),
        ("Employment Contract", "Landlord and Tenant Act"),
        # "offence" is a tag in the Land Act as well.
        ("Police Summons", "Land (Amendment) Act"),
    ],
)
def test_lookup_keeps_tags_inside_the_governing_act(document_type, foreign_act):
    assert _sections(lookup_statutes(document_type), foreign_act) == []


def test_police_summons_leaves_out_internal_police_administration():
    titles = {s["title"] for s in lookup_statutes("Police Summons")}
    assert "Pension qualification" not in titles
    assert "Resignation by police officers" not in titles


@pytest.mark.parametrize("document_type", DOCUMENT_TYPES)
def test_results_are_capped_and_articles_never_crowd_out_the_act(document_type):
    results = lookup_statutes(document_type, context="landlord employer police loan land evict dismiss")
    assert len(results) <= server.MAX_RESULTS

    flags = [_is_constitutional(s) for s in results]
    assert flags == sorted(flags), "constitutional articles come after the statutory sections"

    has_governing_act = bool(server.DOCUMENT_PROFILES[document_type.lower()]["acts"])
    if has_governing_act:
        assert 0 < sum(flags) <= server.MAX_CONSTITUTIONAL


def test_police_summons_gets_the_articles_on_liberty_and_fair_hearing():
    articles = _sections(lookup_statutes("Police Summons"), "Constitution")
    assert {"Article 23", "Article 28"} <= set(articles)
    assert articles[0] == "Article 23"


def test_lookup_unknown_type_falls_back_to_constitutional_rights():
    results = lookup_statutes("Something Unrecognised")
    assert results
    assert all({"rights", "constitutional"} & set(s["tags"]) for s in results)


def test_lookup_context_widens_search():
    results = lookup_statutes("Other", context="my employer wants to dismiss me")
    assert any("employment" in s["tags"] for s in results)
    assert {"Section 58", "Section 65"} <= set(_sections(results, "Employment Act"))


def test_context_words_are_matched_as_whole_words():
    # "rent" is inside "current" and "parent", "land" is inside "landlord".
    unrelated = lookup_statutes("Other", context="the current parent company")
    assert all(_is_constitutional(s) for s in unrelated)

    tenancy = lookup_statutes("Other", context="the landlord")
    assert _sections(tenancy, "Landlord and Tenant Act")
    assert _sections(tenancy, "Land (Amendment) Act") == []


def test_profiles_and_topics_only_name_things_in_the_knowledge_base():
    known_tags = {tag for statute in STATUTE_DB for tag in statute["tags"]}
    known_acts = {statute["act"] for statute in STATUTE_DB}
    sources = list(server.DOCUMENT_PROFILES.values()) + list(server.CONTEXT_TOPICS)

    for source in sources:
        used = set(source["constitutional"]) | set(source.get("core", ())) | set(source.get("related", ()))
        used |= set(source.get("tags", ()))
        assert used <= known_tags, f"unknown tags: {sorted(used - known_tags)}"
        for act in source["acts"]:
            assert any(act in name for name in known_acts), f"no Act matches {act!r}"


def test_lookup_through_the_mcp_client_matches_the_function():
    # The Research Agent reaches the tool through an in-process MCP client.
    async def call():
        async with Client(server.mcp) as client:
            result = await client.call_tool("lookup_statutes", {"document_type": "Eviction Notice", "context": None})
            return result.data

    through_client = asyncio.run(call())
    direct = lookup_statutes("Eviction Notice")
    assert [s["section"] for s in through_client] == [s["section"] for s in direct]


def test_list_acts_is_sorted_and_unique():
    acts = list_acts()
    assert acts == sorted(set(acts))
    assert "Constitution of Uganda 1995" in acts


def test_get_section_found_and_missing():
    first = STATUTE_DB[0]
    assert get_section(first["act"], first["section"]) == first
    assert get_section("No Such Act", "Section 0") is None

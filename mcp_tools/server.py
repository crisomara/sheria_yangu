"""
Sheria Yangu — MCP Server

Exposes the Uganda statute knowledge base as a proper MCP tool
using FastMCP. The Research Agent calls this tool instead of
importing the lookup function directly.

TOOLS EXPOSED:
  - lookup_statutes(document_type, context) → ranked list of statute dicts
  - list_acts() → all Acts in the knowledge base
  - get_section(act_name, section) → one section

To run standalone (for testing):
  python -m mcp_tools.server

To run as part of the pipeline, the Research Agent connects to this
server in-process through a FastMCP client.
"""

import re
from typing import Optional

from fastmcp import FastMCP

from knowledge.uganda_statutes import STATUTE_DB

# Initialise the MCP server
mcp = FastMCP(
    name="sheria-yangu-statutes",
    instructions=(
        "This server provides access to a curated knowledge base of Ugandan "
        "statutory provisions. Use lookup_statutes to find relevant law for a "
        "given document type. Use list_acts to see all Acts covered."
    ),
)

# ── Ranking rules ─────────────────────────────────────────────────────────────
# The knowledge base lists each Act's sections in section order. Returning the
# first matches in that order filled every result with an Act's opening sections
# and dropped the ones a reader most needs (notice periods, unlawful eviction,
# attendance of witnesses). So results are scored and ranked before they are cut.

MAX_RESULTS = 12
# Constitutional articles apply to every document, but they must not crowd out
# the governing Act, so only the best-matching few are kept when an Act applies.
MAX_CONSTITUTIONAL = 3

CORE_WEIGHT = 4  # the sections this kind of document turns on
RELATED_WEIGHT = 2  # useful background from the same Act
CONTEXT_WEIGHT = 2  # a topic the document itself mentions

# One profile per document type the Intake Agent can return.
#   acts            Acts that govern the document, matched against the Act name.
#                   Tags only count inside these Acts, because the same tag means
#                   different things in different Acts ("termination" of a job
#                   and of a tenancy).
#   core, related   knowledge-base tags, weighted as above.
#   constitutional  tags used to pick the constitutional articles that fit.
DOCUMENT_PROFILES: dict[str, dict[str, tuple[str, ...]]] = {
    "employment contract": {
        "acts": ("Employment Act",),
        "core": ("termination", "notice", "dismissal", "wages", "contracts"),
        "related": (
            "misconduct",
            "payment",
            "working hours",
            "overtime",
            "leave",
            "holidays",
            "sick leave",
            "maternity",
            "paternity",
            "benefits",
            "employer duties",
            "discrimination",
            "harassment",
        ),
        "constitutional": (),
    },
    "eviction notice": {
        "acts": ("Landlord and Tenant Act", "Land (Amendment) Act"),
        "core": ("eviction", "termination", "remedy"),
        "related": ("rent", "security deposit", "tenant rights", "occupant", "offence", "court"),
        "constitutional": ("property", "court"),
    },
    "tenancy agreement": {
        "acts": ("Landlord and Tenant Act",),
        "core": ("agreement", "rent", "security deposit", "termination"),
        "related": (
            "eviction",
            "repair",
            "maintenance",
            "habitation",
            "utilities",
            "taxes",
            "tenant rights",
            "prepayment",
            "increase",
            "payment",
            "prohibition",
        ),
        "constitutional": ("property",),
    },
    "police summons": {
        "acts": ("Police (Amendment) Act",),
        "core": ("witness", "investigation", "arrest", "obstruction"),
        "related": ("offence",),
        "constitutional": ("police", "arrest", "criminal", "court"),
    },
    "land agreement": {
        "acts": ("Land (Amendment) Act", "Contracts Act"),
        "core": ("tenancy", "assignment", "occupant", "eviction", "rent"),
        "related": (
            "agreement",
            "capacity",
            "consent",
            "undue influence",
            "fraud",
            "consideration",
            "validity",
            "void",
            "breach",
            "remedy",
            "specific performance",
        ),
        "constitutional": ("property", "land"),
    },
    "loan agreement": {
        "acts": ("Tier 4 Microfinance", "Contracts Act"),
        "core": ("loan", "financial", "guarantee", "indemnity", "undue influence", "fraud"),
        "related": (
            "consent",
            "consideration",
            "legality",
            "validity",
            "void",
            "breach",
            "remedy",
            "time",
            "capacity",
            "agreement",
            "obligation",
        ),
        "constitutional": ("property",),
    },
    # The knowledge base holds no Act written for these two document types. They
    # rest on the constitutional articles, plus anything the context adds. With
    # no governing Act, a core tag counts in any Act.
    "court order": {
        "acts": (),
        "core": ("court",),
        "related": (),
        "constitutional": ("court", "criminal"),
    },
    "government notice": {
        "acts": (),
        "core": (),
        "related": (),
        "constitutional": ("property", "court"),
    },
}

# Topics a document may mention, whatever its type. Each topic points at the
# Acts it concerns, so its tags are scored only there. A keyword matches a whole
# word, or the start of a word when it ends with "*", so "land" does not match
# "landlord" and "rent" does not match "current". Words that are used across
# areas of law ("terminate", "witness", "interest", "title") are left out.
CONTEXT_TOPICS: tuple[dict[str, tuple[str, ...]], ...] = (
    {
        "keywords": ("dismiss*", "redundan*", "fired", "firing", "employer*", "employee*", "employment", "wage*"),
        "acts": ("Employment Act",),
        "tags": ("termination", "dismissal", "notice", "wages"),
        "constitutional": (),
    },
    {
        "keywords": ("evict*", "vacate*"),
        "acts": ("Landlord and Tenant Act", "Land (Amendment) Act"),
        "tags": ("eviction", "termination", "remedy"),
        "constitutional": ("property",),
    },
    {
        "keywords": ("rent", "rental", "landlord*", "tenant*", "tenancy"),
        "acts": ("Landlord and Tenant Act",),
        "tags": ("rent", "security deposit", "termination", "agreement"),
        "constitutional": ("property",),
    },
    {
        "keywords": ("arrest*", "detain*", "detention"),
        "acts": ("Police (Amendment) Act",),
        "tags": ("arrest", "offence"),
        "constitutional": ("police", "arrest", "criminal"),
    },
    {
        "keywords": ("police", "summon*", "investigat*"),
        "acts": ("Police (Amendment) Act",),
        "tags": ("witness", "investigation", "obstruction"),
        "constitutional": ("police", "criminal"),
    },
    {
        "keywords": ("land", "mailo", "kibanja", "plot", "freehold", "leasehold"),
        "acts": ("Land (Amendment) Act",),
        "tags": ("eviction", "occupant", "tenancy", "assignment", "rent"),
        "constitutional": ("land", "property"),
    },
    {
        "keywords": ("loan*", "borrow*", "lender*", "moneylender*", "repay*"),
        "acts": ("Tier 4 Microfinance", "Contracts Act"),
        "tags": ("loan", "financial", "guarantee", "indemnity"),
        "constitutional": (),
    },
)


def _matched_profiles(document_type: str) -> list[dict[str, tuple[str, ...]]]:
    """Every profile whose name appears in the document type."""
    doc_type_lower = document_type.lower()
    return [profile for name, profile in DOCUMENT_PROFILES.items() if name in doc_type_lower]


def _context_topics(context: Optional[str]) -> list[dict[str, tuple[str, ...]]]:
    """The topics that the document's own words point to."""
    if not context:
        return []
    words = set(re.findall(r"[a-z]+", context.lower()))

    def mentioned(keyword: str) -> bool:
        if keyword.endswith("*"):
            return any(word.startswith(keyword[:-1]) for word in words)
        return keyword in words

    return [topic for topic in CONTEXT_TOPICS if any(mentioned(keyword) for keyword in topic["keywords"])]


def _in_acts(statute: dict, acts: tuple[str, ...]) -> bool:
    act_name = statute["act"].lower()
    return any(act.lower() in act_name for act in acts)


def _is_constitutional(statute: dict) -> bool:
    return "constitutional" in statute.get("tags", [])


def _statute_score(statute: dict, profiles: list[dict], topics: list[dict]) -> int:
    tags = set(statute.get("tags", []))
    score = 0
    for profile in profiles:
        if not profile["acts"] or _in_acts(statute, profile["acts"]):
            score += CORE_WEIGHT * len(tags.intersection(profile["core"]))
            score += RELATED_WEIGHT * len(tags.intersection(profile["related"]))
    for topic in topics:
        if _in_acts(statute, topic["acts"]):
            score += CONTEXT_WEIGHT * len(tags.intersection(topic["tags"]))
    return score


@mcp.tool()
def lookup_statutes(document_type: str, context: Optional[str] = None) -> list[dict]:
    """
    Find Ugandan statutory provisions relevant to a given document type.

    Args:
        document_type: The type of legal document being analysed.
                       e.g. 'Employment Contract', 'Eviction Notice',
                       'Police Summons', 'Land Agreement', 'Loan Agreement'
        context:       Optional extra context from the document to help
                       narrow the search (e.g. key terms or parties).

    Returns:
        A list of statute dicts, each containing:
          act, section, title, text, tags
        At most MAX_RESULTS entries, most relevant first: the sections of the
        governing Act that this kind of document turns on, then related
        sections of that Act, then the constitutional articles that fit. An
        unknown document type with no usable context returns the
        constitutional articles only.
    """
    profiles = _matched_profiles(document_type)
    topics = _context_topics(context)

    scored = []
    for position, statute in enumerate(STATUTE_DB):
        if _is_constitutional(statute):
            continue
        score = _statute_score(statute, profiles, topics)
        if score > 0:
            scored.append((-score, position, statute))
    statutory = [statute for _, _, statute in sorted(scored, key=lambda item: item[:2])]

    wanted = {tag for source in profiles + topics for tag in source["constitutional"]}
    ranked_articles = sorted(
        (
            (-len(wanted.intersection(statute.get("tags", []))), position, statute)
            for position, statute in enumerate(STATUTE_DB)
            if _is_constitutional(statute)
        ),
        key=lambda item: item[:2],
    )
    constitutional = [statute for _, _, statute in ranked_articles]
    if any(profile["acts"] for profile in profiles):
        constitutional = constitutional[:MAX_CONSTITUTIONAL]

    return statutory[: MAX_RESULTS - len(constitutional)] + constitutional


@mcp.tool()
def list_acts() -> list[str]:
    """
    List all Acts currently in the Sheria Yangu knowledge base.

    Returns:
        A deduplicated list of Act names and years.
    """
    acts = sorted({statute["act"] for statute in STATUTE_DB})
    return acts


@mcp.tool()
def get_section(act_name: str, section: str) -> Optional[dict]:
    """
    Retrieve a specific section from a specific Act.

    Args:
        act_name: The name of the Act, e.g. 'Employment Act 2006'
        section:  The section identifier, e.g. 'Section 58'

    Returns:
        The statute dict if found, or None.
    """
    for statute in STATUTE_DB:
        if act_name.lower() in statute["act"].lower() and section.lower() in statute["section"].lower():
            return statute
    return None


if __name__ == "__main__":
    # Run the MCP server standalone for testing
    mcp.run()

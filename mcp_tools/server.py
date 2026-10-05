"""
Sheria Yangu — MCP Server

Exposes the Uganda statute knowledge base as a proper MCP tool
using FastMCP. The Research Agent calls this tool instead of
importing the lookup function directly.

TOOLS EXPOSED:
  - lookup_statutes(document_type, context) → list of statute dicts
  - list_acts() → all Acts in the knowledge base

To run standalone (for testing):
  python -m mcp.server

To run as part of the pipeline, the orchestrator starts this
server in-process via FastMCP's lifespan integration.
"""

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
          act, section, title, text, source_url, tags
        Maximum 10 results, always including constitutional rights.
    """
    doc_type_lower = document_type.lower()

    # Map document types to statute tag groups
    tag_map = {
        "employment contract": ["employment", "labour", "termination"],
        "eviction notice": ["tenancy", "landlord", "property"],
        "police summons": ["police", "criminal", "rights", "arrest"],
        "land agreement": ["land", "property", "registration"],
        "tenancy agreement": ["tenancy", "landlord", "property"],
        "loan agreement": ["financial", "contract", "interest"],
        "court order": ["court", "criminal", "rights"],
        "government notice": ["administrative", "rights"],
    }

    applicable_tags = set()
    for key, tags in tag_map.items():
        if key in doc_type_lower:
            applicable_tags.update(tags)

    # If no match, fall back to constitutional rights baseline
    if not applicable_tags:
        applicable_tags = {"rights", "constitutional"}

    # Constitutional rights always included — they apply to every document
    applicable_tags.add("constitutional")

    # Optional: use context keywords to widen the tag net
    if context:
        context_lower = context.lower()
        if any(w in context_lower for w in ["fire", "dismiss", "terminat", "redundan"]):
            applicable_tags.update(["employment", "termination"])
        if any(w in context_lower for w in ["rent", "landlord", "tenant", "vacate"]):
            applicable_tags.update(["tenancy", "landlord"])
        if any(w in context_lower for w in ["arrest", "detain", "police", "charge"]):
            applicable_tags.update(["police", "criminal", "arrest"])
        if any(w in context_lower for w in ["land", "title", "mailo", "lease"]):
            applicable_tags.update(["land", "property"])

    results = [statute for statute in STATUTE_DB if any(tag in statute.get("tags", []) for tag in applicable_tags)]

    return results[:10]


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

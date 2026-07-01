"""
MCP Statute Lookup Tool â€” Sheria Yangu

Maps document types to relevant Ugandan statutory provisions.
Day 2: wrap this as a proper FastMCP server.
"""

from knowledge.uganda_statutes import STATUTE_DB


def lookup_statutes(document_type: str, entities: dict) -> list[dict]:
    doc_type_lower = document_type.lower()

    tag_map = {
        "employment contract":  ["employment", "labour", "termination"],
        "eviction notice":      ["tenancy", "landlord", "property"],
        "police summons":       ["police", "criminal", "rights", "arrest"],
        "land agreement":       ["land", "property", "registration"],
        "tenancy agreement":    ["tenancy", "landlord", "property"],
        "loan agreement":       ["financial", "contract", "interest"],
        "court order":          ["court", "criminal", "rights"],
        "government notice":    ["administrative", "rights"],
    }

    applicable_tags = set()
    for key, tags in tag_map.items():
        if key in doc_type_lower:
            applicable_tags.update(tags)

    if not applicable_tags:
        applicable_tags = {"rights", "constitutional"}

    applicable_tags.add("constitutional")

    results = [
        statute for statute in STATUTE_DB
        if any(tag in statute.get("tags", []) for tag in applicable_tags)
    ]

    return results[:10]

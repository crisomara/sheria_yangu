"""
Agent output schemas - Sheria Yangu

Each agent asks its model for JSON in a fixed shape. A model can still reply
with a missing key, a null, or the wrong type, and the next stage would then
fail with a bare server error. These models check every reply before it is
used. They accept harmless variations (a null list, a number where text is
expected) and reject anything that would change the meaning of the report.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator


def _text(value):
    """Null becomes an empty string and a bare number becomes text."""
    if value is None:
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return value


def _text_list(value):
    """Null becomes an empty list, one string becomes a one-item list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [_text(item) for item in value]
    return value


def _upper_token(value):
    """'high' and 'Short term' become 'HIGH' and 'SHORT_TERM'."""
    if isinstance(value, str):
        return value.strip().upper().replace(" ", "_").replace("-", "_")
    return value


Text = Annotated[str, BeforeValidator(_text)]
TextList = Annotated[list[str], BeforeValidator(_text_list)]


class _AgentModel(BaseModel):
    # Keys the prompt did not ask for are dropped, so nothing unexpected is passed on.
    model_config = ConfigDict(extra="ignore")


class Entities(_AgentModel):
    parties: TextList = []
    dates: TextList = []
    amounts: TextList = []
    obligations: TextList = []
    jurisdiction: Text = "Uganda"


class IntakeOutput(_AgentModel):
    document_type: str = Field(min_length=1)
    extracted_text: Text = ""
    entities: Entities = Field(default_factory=Entities)

    @field_validator("entities", mode="before")
    @classmethod
    def _missing_entities(cls, value):
        return {} if value is None else value


class Statute(_AgentModel):
    act: str = Field(min_length=1)
    section: Text = ""
    title: Text = ""
    text: Text = ""
    relevance: Text = ""


class ResearchOutput(_AgentModel):
    statutes: list[Statute] = []

    @field_validator("statutes", mode="before")
    @classmethod
    def _missing_statutes(cls, value):
        return [] if value is None else value


class Risk(_AgentModel):
    clause: Text = ""
    severity: Annotated[Literal["HIGH", "MEDIUM", "LOW"], BeforeValidator(_upper_token)]
    what_document_says: Text = ""
    what_law_says: Text = ""
    legal_basis: Text = ""
    plain_explanation: Text = ""


class Deadline(_AgentModel):
    description: Text = ""
    date_mentioned: Text = ""
    urgency: Annotated[Literal["IMMEDIATE", "SHORT_TERM", "GENERAL"], BeforeValidator(_upper_token)] = "GENERAL"


class RightsGap(_AgentModel):
    right: Text = ""
    legal_basis: Text = ""
    status_in_document: Text = ""


class AnalysisOutput(_AgentModel):
    risks: list[Risk] = []
    deadlines: list[Deadline] = []
    rights_gaps: list[RightsGap] = []

    @field_validator("risks", "deadlines", "rights_gaps", mode="before")
    @classmethod
    def _missing_list(cls, value):
        return [] if value is None else value


class SynthesisOutput(_AgentModel):
    summary: str = Field(min_length=1)
    your_rights: TextList = []
    next_steps: TextList = []

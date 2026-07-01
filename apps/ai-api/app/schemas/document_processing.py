from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
        extra="forbid",
    )


SourceType = Literal["pdf", "txt", "transcript", "markdown", "software_note"]


class EvidenceLocation(ApiModel):
    page: int | None = Field(default=None, ge=1)
    block: int | None = Field(default=None, ge=0)
    line_start: int | None = Field(default=None, ge=0)
    line_end: int | None = Field(default=None, ge=0)
    char_start: int | None = Field(default=None, ge=0)
    char_end: int | None = Field(default=None, ge=0)


class EvidenceAtom(ApiModel):
    atom_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*:a[0-9]+$")
    document_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    atom_index: int = Field(ge=0)
    atom_type: str = Field(min_length=1)
    source_type: SourceType
    text: str = Field(min_length=1, max_length=1500)
    structured_content: Any = None
    location: EvidenceLocation | None = None
    section_path: list[str] = Field(default_factory=list)
    parent_atom_id: str | None = None
    quality_score: int = Field(ge=0, le=100)
    content_hash: str = Field(pattern=r"^sha256:[A-Fa-f0-9]{64}$")
    access_policy: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CandidateFact(ApiModel):
    subject_name: str = Field(min_length=1)
    subject_type: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object_name: str = Field(min_length=1)
    object_type: str = Field(min_length=1)
    object_properties: dict[str, Any] | None = None
    evidence_atom_ids: list[str] = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    llm_confidence: float = Field(ge=0, le=1)
    approval_score: int = Field(ge=0, le=100)
    valid_from: date | None = None
    valid_until: date | None = None
    ontology_version: str = Field(min_length=1)
    extraction_warnings: list[str] = Field(default_factory=list)

    @field_validator("evidence_atom_ids")
    @classmethod
    def evidence_atom_ids_must_be_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("evidenceAtomIds tekrar eden değer içeremez.")
        return value


class ProcessMetadata(ApiModel):
    file_name: str = Field(min_length=1)
    source_type: SourceType
    parser_version: str = Field(min_length=1)
    ontology_version: str = Field(min_length=1)
    extraction_prompt_version: str | None = None
    processed_at: datetime
    atom_count: int = Field(ge=0)
    candidate_fact_count: int = Field(ge=0)


class ProcessingWarning(ApiModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Literal["info", "warning", "error"]
    evidence_atom_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcessDocumentResponse(ApiModel):
    evidence_atoms: list[EvidenceAtom]
    candidate_facts: list[CandidateFact]
    metadata: ProcessMetadata
    warnings: list[ProcessingWarning] = Field(default_factory=list)

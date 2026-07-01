import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
import yaml
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.document_processing import CandidateFact, EvidenceAtom, ProcessingWarning

PROMPT_VERSION = "extraction_prompt_v1"
MAX_EXTRACTION_CHARS = 12000


class FactExtractionError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def load_ontology() -> dict[str, Any]:
    configured = Path(settings.ontology_path) if settings.ontology_path else None
    container = Path("/app/packages/ontology/demo-ontology.yaml")
    local_candidates = [
        parent / "packages/ontology/demo-ontology.yaml"
        for parent in Path(__file__).resolve().parents
    ]
    path = configured or next(
        (candidate for candidate in [container, *local_candidates] if candidate.exists()),
        container,
    )
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise FactExtractionError("Ontology yüklenemedi.") from exc
    if not isinstance(payload, dict):
        raise FactExtractionError("Ontology object formatında olmalı.")
    required = {"ontologyVersion", "extractionPolicy", "relations"}
    if not required.issubset(payload):
        raise FactExtractionError("Ontology extraction alanları eksik.")
    return payload


async def extract_candidate_facts(
    atoms: list[EvidenceAtom],
) -> tuple[list[CandidateFact], list[ProcessingWarning]]:
    if not atoms:
        return [], []
    if not settings.llm_api_base or not settings.llm_model_name:
        raise FactExtractionError("LLM_API_BASE ve LLM_MODEL_NAME zorunlu.")

    ontology = load_ontology()
    extraction_policy = ontology["extractionPolicy"]
    entity_types = extraction_policy["candidateEntityTypes"]
    relation_types = extraction_policy["candidateRelationTypes"]
    relation_rules = {
        name: {"from": rule["from"], "to": rule["to"]}
        for name, rule in ontology["relations"].items()
        if name in relation_types
    }
    system_prompt = _system_prompt(entity_types, relation_rules)
    candidates: list[CandidateFact] = []
    warnings: list[ProcessingWarning] = []
    for batch in _atom_batches(atoms):
        payload = await _request_facts(system_prompt, batch)
        batch_candidates, batch_warnings = _validate_facts(payload, batch, ontology)
        candidates.extend(batch_candidates)
        warnings.extend(batch_warnings)
    return candidates, warnings


def _atom_batches(atoms: list[EvidenceAtom]) -> list[list[EvidenceAtom]]:
    batches: list[list[EvidenceAtom]] = []
    current: list[EvidenceAtom] = []
    size = 0
    for atom in atoms:
        if current and size + len(atom.text) > MAX_EXTRACTION_CHARS:
            batches.append(current)
            current = []
            size = 0
        current.append(atom)
        size += len(atom.text)
    if current:
        batches.append(current)
    return batches


def _system_prompt(entity_types: list[str], relation_rules: dict[str, Any]) -> str:
    return f"""Extract candidate facts only from supplied evidence atoms.

Rules:
- Output only JSON: {{"facts":[{{...}}]}}.
- Allowed entity types: {json.dumps(entity_types)}.
- Allowed relation direction rules: {json.dumps(relation_rules)}.
- Never invent entity types, relation types, entities, values, dates, or evidence.
- Every fact must reference one or more supplied atomId values in evidenceAtomIds.
- evidenceText must be an exact quote from referenced evidence atom text.
- llmConfidence must be a number from 0 to 1.
- validFrom and validUntil use YYYY-MM-DD when explicit; otherwise null.
- objectProperties must be an object or null.
- Return no fact when evidence does not explicitly support it.

Each fact fields: subjectName, subjectType, predicate, objectName, objectType,
objectProperties, evidenceAtomIds, evidenceText, llmConfidence, validFrom, validUntil.
"""


async def _request_facts(
    system_prompt: str,
    atoms: list[EvidenceAtom],
) -> list[Any]:
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"
    body = {
        "model": settings.llm_model_name,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "evidenceAtoms": [
                            {"atomId": atom.atom_id, "text": atom.text}
                            for atom in atoms
                        ]
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{settings.llm_api_base.rstrip('/')}/chat/completions",
                headers=headers,
                json=body,
            )
    except httpx.RequestError as exc:
        raise FactExtractionError("Fact extraction LLM servisine ulaşılamadı.") from exc
    if not response.is_success:
        raise FactExtractionError(f"Fact extraction LLM HTTP {response.status_code}.")
    try:
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(_strip_code_fence(content))
        facts = parsed["facts"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise FactExtractionError("LLM geçerli fact JSON çıktısı döndürmedi.") from exc
    if not isinstance(facts, list):
        raise FactExtractionError("LLM facts alanı liste değil.")
    return facts


def _validate_facts(
    raw_facts: list[Any],
    atoms: list[EvidenceAtom],
    ontology: dict[str, Any],
) -> tuple[list[CandidateFact], list[ProcessingWarning]]:
    atoms_by_id = {atom.atom_id: atom for atom in atoms}
    policy = ontology["extractionPolicy"]
    allowed_entities = set(policy["candidateEntityTypes"])
    allowed_relations = set(policy["candidateRelationTypes"])
    candidates: list[CandidateFact] = []
    warnings: list[ProcessingWarning] = []

    for index, raw in enumerate(raw_facts):
        reason = _invalid_reason(
            raw, atoms_by_id, allowed_entities, allowed_relations, ontology["relations"]
        )
        if reason:
            warnings.append(_filtered_warning(index, reason))
            continue
        evidence_ids = raw["evidenceAtomIds"]
        evidence_quality = sum(atoms_by_id[item].quality_score for item in evidence_ids) / len(
            evidence_ids
        )
        approval_score = round(raw["llmConfidence"] * 70 + evidence_quality * 0.3)
        try:
            candidates.append(
                CandidateFact(
                    **raw,
                    approvalScore=approval_score,
                    ontologyVersion=ontology["ontologyVersion"],
                    extractionWarnings=[],
                )
            )
        except ValidationError:
            warnings.append(_filtered_warning(index, "schema_validation_failed"))
    return candidates, warnings


def _invalid_reason(
    raw: Any,
    atoms_by_id: dict[str, EvidenceAtom],
    allowed_entities: set[str],
    allowed_relations: set[str],
    relations: dict[str, Any],
) -> str | None:
    if not isinstance(raw, dict):
        return "fact_not_object"
    required = {
        "subjectName",
        "subjectType",
        "predicate",
        "objectName",
        "objectType",
        "evidenceAtomIds",
        "evidenceText",
        "llmConfidence",
    }
    if not required.issubset(raw):
        return "required_field_missing"
    if raw["subjectType"] not in allowed_entities or raw["objectType"] not in allowed_entities:
        return "entity_type_not_allowed"
    predicate = raw["predicate"]
    if predicate not in allowed_relations:
        return "relation_type_not_allowed"
    rule = relations[predicate]
    allowed_to = rule["to"] if isinstance(rule["to"], list) else [rule["to"]]
    if rule["from"] != "*" and raw["subjectType"] != rule["from"]:
        return "relation_direction_invalid"
    if "*" not in allowed_to and raw["objectType"] not in allowed_to:
        return "relation_direction_invalid"
    evidence_ids = raw["evidenceAtomIds"]
    if not isinstance(evidence_ids, list) or not evidence_ids:
        return "evidence_required"
    if len(evidence_ids) != len(set(evidence_ids)):
        return "evidence_ids_not_unique"
    if any(item not in atoms_by_id for item in evidence_ids):
        return "evidence_atom_not_found"
    evidence_text = raw["evidenceText"]
    if not isinstance(evidence_text, str) or not any(
        evidence_text in atoms_by_id[item].text for item in evidence_ids
    ):
        return "evidence_text_not_supported"
    confidence = raw["llmConfidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return "llm_confidence_invalid"
    if not 0 <= confidence <= 1:
        return "llm_confidence_invalid"
    return None


def _filtered_warning(index: int, reason: str) -> ProcessingWarning:
    return ProcessingWarning(
        code="CANDIDATE_FACT_FILTERED",
        message="Ontology, schema veya evidence kontrolünü geçemeyen fact filtrelendi.",
        severity="warning",
        metadata={"factIndex": index, "reason": reason},
    )


def _strip_code_fence(value: str) -> str:
    text = value.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1 :] if first_newline >= 0 else text
        if text.endswith("```"):
            text = text[:-3]
    start = text.find("{")
    end = text.rfind("}")
    return text[start : end + 1] if start >= 0 and end >= start else text.strip()

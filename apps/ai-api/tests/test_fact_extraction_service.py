import unittest

from app.schemas.document_processing import EvidenceAtom
from app.services.fact_extraction_service import _system_prompt, _validate_facts


def evidence_atom() -> EvidenceAtom:
    return EvidenceAtom(
        atomId="sales:a001",
        documentId="doc-1",
        sourceId="sales",
        sourceVersion="v1",
        atomIndex=0,
        atomType="paragraph",
        sourceType="txt",
        text="ABC Boya'nın 2026 satış hedefi 300 tondur.",
        structuredContent=None,
        location=None,
        sectionPath=[],
        parentAtomId=None,
        qualityScore=90,
        contentHash="sha256:" + "a" * 64,
        accessPolicy="internal",
        metadata={},
    )


ONTOLOGY = {
    "ontologyVersion": "demo_ontology_v2",
    "extractionPolicy": {
        "candidateEntityTypes": ["Customer", "SalesTarget"],
        "candidateRelationTypes": ["hasTarget"],
    },
    "relations": {"hasTarget": {"from": "Customer", "to": "SalesTarget"}},
}


class FactExtractionTests(unittest.TestCase):
    def test_valid_fact_gets_deterministic_approval_score(self) -> None:
        raw = {
            "subjectName": "ABC Boya",
            "subjectType": "Customer",
            "predicate": "hasTarget",
            "objectName": "300 ton",
            "objectType": "SalesTarget",
            "objectProperties": {"year": 2026, "amount": 300, "unit": "ton"},
            "evidenceAtomIds": ["sales:a001"],
            "evidenceText": "ABC Boya'nın 2026 satış hedefi 300 tondur.",
            "llmConfidence": 0.9,
            "validFrom": "2026-01-01",
            "validUntil": "2026-12-31",
        }
        candidates, warnings = _validate_facts([raw], [evidence_atom()], ONTOLOGY)
        self.assertEqual(warnings, [])
        self.assertEqual(candidates[0].approval_score, 90)
        self.assertEqual(candidates[0].ontology_version, "demo_ontology_v2")

    def test_ontology_direction_violation_is_filtered(self) -> None:
        raw = {
            "subjectName": "300 ton",
            "subjectType": "SalesTarget",
            "predicate": "hasTarget",
            "objectName": "ABC Boya",
            "objectType": "Customer",
            "evidenceAtomIds": ["sales:a001"],
            "evidenceText": "ABC Boya'nın 2026 satış hedefi 300 tondur.",
            "llmConfidence": 0.9,
        }
        candidates, warnings = _validate_facts([raw], [evidence_atom()], ONTOLOGY)
        self.assertEqual(candidates, [])
        self.assertEqual(warnings[0].metadata["reason"], "relation_direction_invalid")

    def test_prompt_contains_allowed_types_and_no_invention_rule(self) -> None:
        prompt = _system_prompt(
            ["Customer", "SalesTarget"],
            {"hasTarget": {"from": "Customer", "to": "SalesTarget"}},
        )
        self.assertIn("Never invent", prompt)
        self.assertIn("hasTarget", prompt)
        self.assertIn("evidenceAtomIds", prompt)


if __name__ == "__main__":
    unittest.main()

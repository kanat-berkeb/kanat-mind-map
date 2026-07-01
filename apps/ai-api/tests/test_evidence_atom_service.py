import unittest

from app.services.document_parser_service import ParsedBlock, _parse_markdown, _parse_text
from app.services.evidence_atom_service import build_evidence_atoms
from app.schemas.document_processing import CandidateFact, ProcessDocumentResponse
from app.services.semantic_atom_service import (
    SemanticPiece,
    _merge_short_pieces,
    deterministic_segments,
)


class EvidenceAtomTests(unittest.TestCase):
    def test_same_input_produces_same_atom_ids(self) -> None:
        block = ParsedBlock(text="ABC Boya 2026 hedefini 300 ton olarak belirledi.", block=0)
        pieces = [SemanticPiece(block, block.text, 0, len(block.text))]

        first = build_evidence_atoms("hedef.txt", b"source", "txt", pieces)
        second = build_evidence_atoms("hedef.txt", b"source", "txt", pieces)

        self.assertEqual([atom.atom_id for atom in first], [atom.atom_id for atom in second])
        self.assertEqual(first[0].atom_index, 0)
        self.assertEqual(first[0].text, block.text)

    def test_short_neighbor_is_merged_inside_same_block(self) -> None:
        block = ParsedBlock(text="Kısa cümle. Bu devam cümlesi gerekli bağlamı taşır.")
        pieces = [
            SemanticPiece(block, "Kısa cümle.", 0, 12),
            SemanticPiece(block, "Bu devam cümlesi gerekli bağlamı taşır.", 13, 55),
        ]

        merged = _merge_short_pieces(pieces)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].text, block.text)

    def test_markdown_heading_becomes_section_path(self) -> None:
        blocks = _parse_markdown("# Organizasyon\n## Satış\nABC Boya hedef belirledi.\n")
        self.assertEqual(blocks[0].section_path, ["Organizasyon", "Satış"])

    def test_transcript_speaker_is_preserved(self) -> None:
        blocks = _parse_text("Ayşe: Hedef 300 ton.\nMehmet: Risk yüksek.\n")
        self.assertEqual([block.atom_type for block in blocks], ["speaker_turn", "speaker_turn"])
        self.assertEqual(blocks[0].metadata["speaker"], "Ayşe")
        self.assertEqual(blocks[0].text, "Ayşe: Hedef 300 ton.")

    def test_fallback_splits_long_block_without_changing_text(self) -> None:
        source = " ".join(["ABC Boya hedef belirledi."] * 100)
        pieces = deterministic_segments([ParsedBlock(text=source)])
        self.assertTrue(all(len(piece.text) <= 1500 for piece in pieces))
        self.assertEqual(" ".join(piece.text for piece in pieces), source)

    def test_api_models_serialize_contract_fields_as_camel_case(self) -> None:
        schema = ProcessDocumentResponse.model_json_schema(by_alias=True)
        self.assertIn("evidenceAtoms", schema["properties"])
        self.assertIn("candidateFacts", schema["properties"])
        candidate_schema = CandidateFact.model_json_schema(by_alias=True)
        self.assertIn("evidenceAtomIds", candidate_schema["properties"])
        self.assertIn("approvalScore", candidate_schema["properties"])


if __name__ == "__main__":
    unittest.main()

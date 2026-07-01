import hashlib
import re
from pathlib import Path

from app.schemas.document_processing import EvidenceAtom, EvidenceLocation, SourceType
from app.services.document_parser_service import ParsedBlock
from app.services.semantic_atom_service import SemanticPiece

MIN_ATOM_LENGTH = 80


def build_evidence_atoms(
    file_name: str,
    content: bytes,
    source_type: SourceType,
    pieces: list[SemanticPiece],
    segmentation: str = "llm_semantic_v1",
) -> list[EvidenceAtom]:
    source_hash = hashlib.sha256(content).hexdigest()
    source_key = f"{_slug(Path(file_name).stem)}-{source_hash[:12]}"
    source_version = f"sha256:{source_hash}"
    atoms: list[EvidenceAtom] = []
    for index, piece in enumerate(pieces):
        block = piece.block
        text = piece.text
        atom_id = f"{source_key}:a{index + 1:03d}"
        atoms.append(
            EvidenceAtom(
                atom_id=atom_id,
                document_id=f"upload:{source_key}",
                source_id=source_key,
                source_version=source_version,
                atom_index=index,
                atom_type=block.atom_type,
                source_type=source_type,
                text=text,
                structured_content=None,
                location=EvidenceLocation(
                    page=block.page,
                    block=block.block,
                    char_start=(
                        block.char_start + piece.relative_start
                        if block.char_start is not None
                        else None
                    ),
                    char_end=(
                        block.char_start + piece.relative_end
                        if block.char_start is not None
                        else None
                    ),
                ),
                section_path=block.section_path,
                parent_atom_id=None,
                quality_score=_quality_score(text, block),
                content_hash=f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}",
                access_policy="internal",
                metadata={**block.metadata, "segmentation": segmentation},
            )
        )
    return atoms


def _quality_score(text: str, block: ParsedBlock) -> int:
    score = 55
    if len(text) >= MIN_ATOM_LENGTH:
        score += 15
    if text.endswith((".", "!", "?")):
        score += 10
    if block.page is not None or block.char_start is not None:
        score += 10
    if block.section_path:
        score += 10
    return min(score, 100)


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._").lower()
    return slug or "document"

import hashlib
import re
from pathlib import Path

from app.schemas.document_processing import EvidenceAtom, EvidenceLocation, SourceType
from app.services.document_parser_service import ParsedBlock

MAX_ATOM_LENGTH = 1500
MIN_ATOM_LENGTH = 80


def build_evidence_atoms(
    file_name: str,
    content: bytes,
    source_type: SourceType,
    blocks: list[ParsedBlock],
) -> list[EvidenceAtom]:
    source_hash = hashlib.sha256(content).hexdigest()
    source_key = f"{_slug(Path(file_name).stem)}-{source_hash[:12]}"
    source_version = f"sha256:{source_hash}"
    pieces = _split_and_merge(blocks)

    atoms: list[EvidenceAtom] = []
    for index, (block, text) in enumerate(pieces):
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
                    char_start=block.char_start,
                    char_end=block.char_end,
                ),
                section_path=block.section_path,
                parent_atom_id=None,
                quality_score=_quality_score(text, block),
                content_hash=f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}",
                access_policy="internal",
                metadata=block.metadata,
            )
        )
    return atoms


def _split_and_merge(blocks: list[ParsedBlock]) -> list[tuple[ParsedBlock, str]]:
    pieces: list[tuple[ParsedBlock, str]] = []
    for block in blocks:
        for text in _split_text(" ".join(block.text.split())):
            if text:
                pieces.append((block, text))

    merged: list[tuple[ParsedBlock, str]] = []
    for block, text in pieces:
        if (
            len(text) < MIN_ATOM_LENGTH
            and merged
            and merged[-1][0].page == block.page
            and merged[-1][0].section_path == block.section_path
            and len(merged[-1][1]) + 1 + len(text) <= MAX_ATOM_LENGTH
        ):
            previous_block, previous_text = merged[-1]
            merged[-1] = (previous_block, f"{previous_text} {text}")
        else:
            merged.append((block, text))
    return merged


def _split_text(text: str) -> list[str]:
    if len(text) <= MAX_ATOM_LENGTH:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > MAX_ATOM_LENGTH:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_words(sentence))
        elif not current:
            current = sentence
        elif len(current) + 1 + len(sentence) <= MAX_ATOM_LENGTH:
            current = f"{current} {sentence}"
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def _split_words(text: str) -> list[str]:
    chunks: list[str] = []
    current = ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > MAX_ATOM_LENGTH:
            chunks.append(current)
            current = word
        else:
            current = word if not current else f"{current} {word}"
    if current:
        chunks.append(current)
    return chunks


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

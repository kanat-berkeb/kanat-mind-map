import re
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path


PDF_LIST_MARKER = re.compile(r"^([•●▪◦*-])\s+")


@dataclass(frozen=True)
class ParsedBlock:
    text: str
    atom_type: str = "paragraph"
    page: int | None = None
    block: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    section_path: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


def parse_document(file_name: str, content: bytes) -> list[ParsedBlock]:
    if not content:
        raise ValueError("Dosya boş.")

    suffix = Path(file_name).suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(content)
    if suffix in {".txt", ".md"}:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("TXT/MD dosyası UTF-8 olmalı.") from exc
        return _parse_markdown(text) if suffix == ".md" else _parse_text(text)

    raise ValueError("Desteklenmeyen dosya. Yalnız PDF, TXT ve MD kabul edilir.")


def _parse_pdf(content: bytes) -> list[ParsedBlock]:
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ValueError("PDF okunamadı.") from exc

    blocks: list[ParsedBlock] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        blocks.extend(_pdf_blocks(text, page_number))
    return blocks


def _pdf_blocks(text: str, page_number: int) -> list[ParsedBlock]:
    blocks: list[ParsedBlock] = []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for line in normalized.splitlines():
        value = " ".join(line.split())
        if not value:
            continue

        metadata = {"parser": "pypdf"}
        atom_type = "paragraph"
        marker = PDF_LIST_MARKER.match(value)
        if marker:
            metadata["listMarker"] = marker.group(1)
            atom_type = "list_item"
            value = value[marker.end() :]

        blocks.append(
            ParsedBlock(
                text=value,
                atom_type=atom_type,
                page=page_number,
                block=len(blocks),
                metadata=metadata,
            )
        )
    return blocks


def _parse_text(text: str) -> list[ParsedBlock]:
    blocks: list[ParsedBlock] = []
    cursor = 0
    for index, paragraph in enumerate(_paragraphs(text)):
        start = text.find(paragraph, cursor)
        start = cursor if start < 0 else start
        end = start + len(paragraph)
        blocks.append(
            ParsedBlock(
                text=paragraph,
                block=index,
                char_start=start,
                char_end=end,
            )
        )
        cursor = end
    return blocks


def _parse_markdown(text: str) -> list[ParsedBlock]:
    blocks: list[ParsedBlock] = []
    headings: list[str] = []
    paragraph: list[str] = []
    paragraph_start = 0
    offset = 0

    def flush() -> None:
        nonlocal paragraph, paragraph_start
        value = "\n".join(paragraph).strip()
        if value:
            blocks.append(
                ParsedBlock(
                    text=value,
                    block=len(blocks),
                    char_start=paragraph_start,
                    char_end=paragraph_start + len(value),
                    section_path=headings.copy(),
                )
            )
        paragraph = []

    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").startswith(" "):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            headings[level - 1 :] = [title]
        elif not stripped:
            flush()
        else:
            if not paragraph:
                paragraph_start = offset
            paragraph.append(stripped)
        offset += len(line)
    flush()
    return blocks


def _paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return [" ".join(part.split()) for part in normalized.split("\n\n") if part.strip()]

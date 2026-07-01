from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.document_processing import (
    ProcessDocumentResponse,
    ProcessMetadata,
    ProcessingWarning,
    SourceType,
)
from app.services.document_parser_service import parse_document
from app.services.evidence_atom_service import build_evidence_atoms
from app.services.semantic_atom_service import (
    PROMPT_VERSION,
    SemanticAtomError,
    deterministic_segments,
    segment_blocks,
)

router = APIRouter(tags=["document-processing"])

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(
    file: Annotated[UploadFile, File()],
    source_type: Annotated[SourceType, Form(alias="sourceType")],
) -> ProcessDocumentResponse:
    file_name = Path(file.filename or "document").name
    content = await file.read(MAX_FILE_SIZE + 1)
    await file.close()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Dosya 10 MB sınırını aşıyor.")

    try:
        blocks = parse_document(file_name, content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    warnings: list[ProcessingWarning] = []
    segmentation_version = "llm-semantic-v1"
    try:
        pieces = await segment_blocks(blocks)
    except SemanticAtomError as exc:
        pieces = deterministic_segments(blocks)
        segmentation_version = "deterministic-fallback-v1"
        warnings.append(
            ProcessingWarning(
                code="SEMANTIC_SEGMENTATION_FALLBACK",
                message="LLM segmentasyonu başarısız; deterministik parçalama kullanıldı.",
                severity="warning",
                metadata={"errorType": type(exc).__name__},
            )
        )

    atoms = build_evidence_atoms(
        file_name,
        content,
        source_type,
        pieces,
        segmentation=segmentation_version,
    )

    if not atoms:
        warnings.append(
            ProcessingWarning(
                code="NO_TEXT_EXTRACTED",
                message="Dosyadan işlenebilir metin çıkarılamadı.",
                severity="warning",
            )
        )

    return ProcessDocumentResponse(
        evidence_atoms=atoms,
        candidate_facts=[],
        metadata=ProcessMetadata(
            file_name=file_name,
            source_type=source_type,
            parser_version=f"document-parser-v1+{segmentation_version}",
            ontology_version="demo-v1",
            extraction_prompt_version=PROMPT_VERSION,
            processed_at=datetime.now(timezone.utc),
            atom_count=len(atoms),
            candidate_fact_count=0,
        ),
        warnings=warnings,
    )

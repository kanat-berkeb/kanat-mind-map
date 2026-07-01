import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.services.document_parser_service import ParsedBlock

PROMPT_VERSION = "semantic-atom-v1"
MAX_BATCH_CHARS = 6000
MAX_ATOM_LENGTH = 1500
PreparedBlock = tuple[int, ParsedBlock, str, int]

SYSTEM_PROMPT = """You split source text into evidence atoms.

An evidence atom is the smallest source span that preserves enough context to support one
meaningful proposition. Prefer boundaries useful for these ontology relations:
managedBy, locatedIn, interestedIn, hasTarget, hasRisk, memberOf, ownsService,
partOf, dependsOn, decidedIn, affects, mentions, holdsRole, hasRoleAssignment.

Rules:
- Use only exact text copied from each input block.
- Never summarize, rewrite, correct, translate, infer, or add text.
- Preserve all source text exactly once and in original order within each block.
- Split independent propositions when grammar still leaves each span understandable.
- Keep dependent clauses together when splitting would destroy subject or context.
- Input blocks may be titles, headings, labels, or list items; never omit any block.
- Each atom must be non-empty and at most 1500 characters.
- Return only JSON: {"atoms":[{"blockId":0,"text":"exact source span"}]}.
- Return at least one atom for every non-empty block.
"""


class SemanticAtomError(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticPiece:
    block: ParsedBlock
    text: str
    relative_start: int
    relative_end: int


async def segment_blocks(blocks: list[ParsedBlock]) -> list[SemanticPiece]:
    if not settings.llm_api_base or not settings.llm_model_name:
        raise SemanticAtomError("LLM_API_BASE ve LLM_MODEL_NAME zorunlu.")

    prepared = _prepare_blocks(blocks)
    pieces: list[SemanticPiece] = []
    async with httpx.AsyncClient(timeout=300) as client:
        for batch in _batches(prepared):
            raw_atoms = await _request_atoms(client, batch)
            pieces.extend(_validate_atoms(batch, raw_atoms))
    return pieces


def _batches(
    blocks: list[PreparedBlock],
) -> list[list[PreparedBlock]]:
    batches: list[list[PreparedBlock]] = []
    current: list[PreparedBlock] = []
    current_size = 0
    for item in blocks:
        size = len(item[2])
        if current and current_size + size > MAX_BATCH_CHARS:
            batches.append(current)
            current = []
            current_size = 0
        current.append(item)
        current_size += size
    if current:
        batches.append(current)
    return batches


async def _request_atoms(
    client: httpx.AsyncClient,
    batch: list[PreparedBlock],
) -> list[dict[str, Any]]:
    headers = {"Content-Type": "application/json"}
    if settings.llm_api_key:
        headers["Authorization"] = f"Bearer {settings.llm_api_key}"

    request_url = f"{settings.llm_api_base.rstrip('/')}/chat/completions"
    request_payload = {
        "model": settings.llm_model_name,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "blocks": [
                            {"blockId": block_id, "text": text}
                            for block_id, _, text, _ in batch
                        ]
                    },
                    ensure_ascii=False,
                ),
            },
        ],
    }
    print("vLLM request URL:", request_url, flush=True)
    print(
        "vLLM request payload:",
        json.dumps(request_payload, ensure_ascii=False),
        flush=True,
    )

    try:
        response = await client.post(
            request_url,
            headers=headers,
            json=request_payload,
        )
    except httpx.RequestError as exc:
        raise SemanticAtomError(f"LLM servisine ulaşılamadı: {exc}") from exc
    if not response.is_success:
        raise SemanticAtomError(
            f"LLM HTTP {response.status_code}: {response.text[:300]}"
        )

    try:
        message = response.json()["choices"][0]["message"]["content"]
        print("vLLM response content:", message, flush=True)
        payload = json.loads(_strip_code_fence(message))
        atoms = payload["atoms"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise SemanticAtomError("LLM geçerli atom JSON çıktısı döndürmedi.") from exc
    if not isinstance(atoms, list):
        raise SemanticAtomError("LLM atoms alanı liste değil.")
    return atoms


def _validate_atoms(
    batch: list[PreparedBlock],
    atoms: list[dict[str, Any]],
) -> list[SemanticPiece]:
    grouped: dict[int, list[str]] = {
        block_id: [] for block_id, _, _, _ in batch
    }
    for atom in atoms:
        if not isinstance(atom, dict):
            raise SemanticAtomError("LLM atom kaydı object değil.")
        block_id = atom.get("blockId")
        text = atom.get("text")
        if (
            not isinstance(block_id, int)
            or block_id not in grouped
            or not isinstance(text, str)
            or not text
        ):
            raise SemanticAtomError("LLM atom blockId/text alanı geçersiz.")
        if len(text) > MAX_ATOM_LENGTH:
            raise SemanticAtomError("LLM 1500 karakterden uzun atom döndürdü.")
        grouped[block_id].append(text)

    result: list[SemanticPiece] = []
    for block_id, block, source_text, base_offset in batch:
        block_atoms = grouped[block_id]
        if not block_atoms or " ".join(block_atoms) != source_text:
            raise SemanticAtomError(
                f"LLM block {block_id} metnini değiştirdi, eksiltti veya çoğalttı."
            )
        cursor = 0
        for text in block_atoms:
            start = source_text.find(text, cursor)
            if start < 0:
                raise SemanticAtomError(f"LLM block {block_id} sırasını değiştirdi.")
            end = start + len(text)
            result.append(
                SemanticPiece(
                    block=block,
                    text=text,
                    relative_start=base_offset + start,
                    relative_end=base_offset + end,
                )
            )
            cursor = end + 1
    return result


def _prepare_blocks(blocks: list[ParsedBlock]) -> list[PreparedBlock]:
    prepared: list[PreparedBlock] = []
    next_id = 0
    for block in blocks:
        source = " ".join(block.text.split())
        cursor = 0
        while cursor < len(source):
            remaining = len(source) - cursor
            if remaining <= MAX_BATCH_CHARS:
                end = len(source)
            else:
                window_end = cursor + MAX_BATCH_CHARS
                sentence_end = source.rfind(
                    ". ", cursor + MAX_BATCH_CHARS // 2, window_end
                )
                if sentence_end >= 0:
                    end = sentence_end + 1
                else:
                    word_end = source.rfind(" ", cursor + 1, window_end)
                    end = word_end if word_end > cursor else window_end
            text = source[cursor:end]
            prepared.append((next_id, block, text, cursor))
            next_id += 1
            cursor = end + 1 if end < len(source) and source[end] == " " else end
    return prepared


def _strip_code_fence(value: str) -> str:
    text = value.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1 :] if first_newline >= 0 else text
        if text.endswith("```"):
            text = text[:-3]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    return text[start : end + 1] if start >= 0 and end >= start else text

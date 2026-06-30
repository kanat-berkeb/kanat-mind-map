# System Architecture

## 1. Genel bakış

`kanat-mind-map`, evidence-first living memory mimarisine göre tasarlanır.

```text
Raw Sources
→ Evidence Archive
→ Evidence Atom Store
→ Retrieval Substrate
→ Candidate Knowledge Layer
→ Validation Engine
→ Curation Workbench
→ Graph Patch
→ Curated Knowledge Graph
→ Semantic Memory
→ Working Memory
→ LLM / Agent / Ask
```

Bu yapıdaki en önemli ayrım şudur:

```text
Evidence Archive memory değildir.
Vector/lexical index memory değildir.
Candidate fact truth değildir.
Curated KG tek başına kullanıcıya uygun öz hafıza değildir.
Semantic Memory, onaylı graph'tan üretilmiş öz bilgi katmanıdır.
```

## 2. Servis sınırları

```text
apps/web
  Next.js UI.
  Sadece apps/api ile konuşur.

apps/api
  NestJS sistem sınırı.
  Veri sahipliği, workflow, review, validation orchestration, publish ve ask burada yönetilir.

apps/ai-api
  FastAPI stateless document/LLM processing servisi.
  Dosya parse eder, evidence atom ve candidate fact önerisi döner.
  DB'ye yazmaz.

PostgreSQL
  Document, EvidenceAtom, CandidateFact, ValidationResult, ReviewDecision, GraphPatch,
  ConflictRecord, SemanticMemoryItem, audit ve workflow metadata kaynağıdır.

Neo4j
  Sadece curated/published graph bilgisini tutar.
  Candidate veya rejected bilgi Neo4j'ye yazılmaz.
```

Değişmez sınır:

```text
Next.js → NestJS → FastAPI
NestJS → PostgreSQL
NestJS → Neo4j
```

## 3. Katmanlar

### 3.1 Evidence Archive

Ham kaynakların ve evidence atomların korunduğu arşivdir. Memory değildir.

Kapsar:

```text
raw files
source metadata
parsed documents
evidence atoms
source versions
checksum
ACL
parser metadata
```

MVP implementasyonu:

```text
local file storage + PostgreSQL metadata
```

Future implementasyon:

```text
MinIO/S3 + object versioning + richer document model
```

### 3.2 Retrieval Substrate

Kanıt bulma altyapısıdır. Memory değildir.

MVP implementasyonu:

```text
PostgreSQL metadata filters
basic text search
Neo4j current neighborhood query
```

Future implementasyon:

```text
pgvector/Qdrant
OpenSearch
reranker
entity mention index
evidence graph
```

### 3.3 Candidate Knowledge Layer

LLM/agent çıktılarının tutulduğu öneri katmanıdır.

Kapsar:

```text
CandidateFact
CandidateClaim
CandidateConflict
GraphPatch proposal
OntologyProposal
```

Kural:

```text
Candidate bilgi kullanıcıya kesin bilgi gibi sunulmaz.
Candidate bilgi Neo4j'ye doğrudan yazılmaz.
```

### 3.4 Validation Engine

Candidate bilgiyi curated KG'ye girmeden önce kontrol eder.

Kontroller:

```text
schema validation
ontology validation
relation direction validation
entity resolution validation
evidence support validation
temporal validation
source authority validation
conflict validation
ACL validation
business rule validation
review policy validation
```

### 3.5 Curation Workbench

İnsan review ekranıdır.

Kullanıcı şunları yapabilir:

```text
approve
reject
edit
merge entity
resolve conflict
expire fact
retract fact
approve graph patch
reject graph patch
```

### 3.6 Graph Patch

Curated KG değişiklikleri doğrudan tek tek fact publish etmek yerine patch olarak paketlenir.

Örnek:

```json
{
  "patchId": "patch_role_change_001",
  "operations": [
    { "op": "EXPIRE_ASSERTION", "assertionId": "assert_001" },
    { "op": "ADD_ASSERTION", "subject": "Mehmet Demir", "predicate": "holdsRole", "object": "Satış Başkanı" }
  ]
}
```

Bu model eski bilgi ezme, conflict çözme ve audit için gereklidir.

### 3.7 Curated Knowledge Graph

Onaylı, evidence-linked, ontology-compliant structured gerçekliktir.

Neo4j sadece bu katmanı tutar.

Kural:

```text
Only approved graph patches can modify Curated KG.
```

### 3.8 Semantic Memory

Asıl memory katmanıdır.

Curated KG'den türetilmiş öz bilgi kartlarını tutar.

Örnek:

```text
Güncel organizasyon bilgisine göre satış başkanı Mehmet Demir,
satış başkan yardımcısı Ayşe Kaya'dır. Önceki kayıtta Ayşe satış başkanı olarak görünüyordu.
```

Semantic memory ham source değil, curated state'tir.

### 3.9 Working Memory

LLM/agent çağrısı için hazırlanan küçük görev paketidir.

İçerir:

```text
task instruction
relevant evidence atoms
ontology subset
current semantic memory
existing curated facts
conflict notes
output schema
```

Tüm memory veya tüm graph LLM'e verilmez.

## 4. Write path

```text
Upload
→ Document record
→ FastAPI parse
→ Evidence atoms
→ Candidate facts
→ Validation results
→ Graph patch proposal
→ Human review
→ Curated KG publish
→ Semantic memory update
```

## 5. Read path

```text
User question
→ intent/entity detection
→ ACL check
→ semantic memory retrieval
→ curated KG fallback
→ evidence retrieval
→ working memory pack
→ LLM/source-grounded answer
```

## 6. Data ownership

| Veri | Ana kaynak |
|---|---|
| Raw file | Local storage MVP, object store future |
| Document metadata | PostgreSQL |
| Evidence atoms | PostgreSQL |
| Candidate facts | PostgreSQL |
| Validation results | PostgreSQL |
| Review decisions | PostgreSQL |
| Graph patches | PostgreSQL |
| Published assertions | PostgreSQL + Neo4j projection |
| Curated graph | Neo4j |
| Semantic memory | PostgreSQL |
| Ontology version | packages/ontology + PostgreSQL metadata |

## 7. API sınırları

Örnek endpoint grupları:

```text
POST /documents/upload
POST /documents/:id/extract
GET  /documents/:id/evidence-atoms
GET  /facts/candidates
GET  /facts/:id/validation-results
POST /facts/:id/validate
POST /facts/:id/approve
POST /facts/:id/reject
POST /graph-patches/:id/approve
POST /graph-patches/:id/publish
GET  /graph
GET  /memory
GET  /memory/:id
POST /ask
```

## 8. Mimari kararlar

```text
FastAPI stateless kalır.
NestJS workflow sahibi olur.
PostgreSQL review ve lifecycle source of truth olur.
Neo4j yalnızca published graph projection olur.
Semantic memory PostgreSQL'de tutulur.
LLM sadece working memory pack görür.
```

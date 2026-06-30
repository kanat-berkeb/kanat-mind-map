# Codex Task Plan

## 1. Amaç

Bu plan mevcut FastAPI, NestJS, Next.js ve container temellerinin bulunduğu `kanat-mind-map` projesini yeni living memory mimarisine taşımak için hazırlanmıştır.

Bu plan sıfırdan framework kurdurmak yerine mevcut projeyi aşamalı olarak düzenlemeyi hedefler.

## 2. Değişmez Codex kuralları

```text
Commit atma.
Tek seferde tüm projeyi değiştirme.
Mevcut servis sınırlarını bozma.
FastAPI veritabanına yazmasın.
Next.js yalnızca NestJS ile konuşsun.
LLM output doğrudan Neo4j'ye yazılmasın.
Her task sonunda çalıştırılacak komutları yaz.
Yeni dependency ekliyorsan nedenini açıkla.
MVP ve future ayrımını koru.
```

## 3. Faz 0 — Dokümanları yerleştir

### Task 0.1 — Docs setini güncelle

Amaç: Yeni mimari dokümanlarını repo içine almak.

Dosyalar:

```text
docs/project-overview.md
docs/mvp-demo-plan.md
docs/system-architecture.md
docs/memory-taxonomy.md
docs/evidence-atom-rules.md
docs/fact-lifecycle.md
docs/data-model-spec.md
docs/ontology-governance.md
docs/validation-review-policy.md
docs/codex-task-plan.md
docs/development-guidelines.md
docs/smoke-test-checklist.md
```

Kabul kriteri:

```text
Docs klasörü yeni mimariyi anlatıyor.
Memory, archive, candidate, curated KG ayrımı net.
Eski tasks_info tekrarı kaldırılmış veya development-guidelines'a dönüştürülmüş.
```

Codex prompt:

```text
Repo docs klasörünü kanat-mind-map living memory mimarisine göre güncelle.
Verilen markdown dosyalarını docs altına yerleştir.
Eski architecture.md varsa system-architecture.md adına taşı.
Eski demo-plan.md varsa mvp-demo-plan.md adına taşı.
Eski proje_bilgileri.md varsa project-overview.md adına taşı.
Eski tasks_info.md varsa development-guidelines.md olarak düzenle ve task tekrarlarını kaldır.
Kod değiştirme.
Commit atma.
```

## 4. Faz 1 — Ontology ve contracts

### Task 1.1 — Ontology genişletme

Amaç: Mevcut demo ontology'yi living memory kavramlarıyla genişletmek.

Eklenecek entity tipleri:

```text
Role
RoleAssignment
Department
EvidenceAtom
Conflict
GraphPatch
SemanticMemoryItem
```

Eklenecek relation tipleri:

```text
holdsRole
hasRoleAssignment
supportedBy
supersedes
retractedBy
summarizes
```

Kabul kriteri:

```text
packages/ontology/demo-ontology.yaml güncellenmiş.
Her relation from/to, evidence_required ve review policy taşıyor.
SalesPresident maxActiveHolders=1 kuralı eklenmiş.
```

### Task 1.2 — Contract schema dosyaları

Amaç: Servisler arası JSON contract'ları netleştirmek.

Dosyalar:

```text
packages/contracts/evidence-atom.schema.json
packages/contracts/candidate-fact.schema.json
packages/contracts/validation-result.schema.json
packages/contracts/graph-patch.schema.json
packages/contracts/semantic-memory-item.schema.json
```

Kabul kriteri:

```text
Contract field naming camelCase.
FastAPI response ve NestJS DTO'ları bu contract'lara yakın.
```

## 5. Faz 2 — PostgreSQL data model update

### Task 2.1 — Prisma modellerini living memory'ye hazırla

Amaç: Candidate-only eski modeli genişletmek.

Eklenecek/güncellenecek modeller:

```text
Document
EvidenceAtom
CandidateFact
ValidationResult
GraphPatch
PublishedAssertion
SemanticMemoryItem
```

Kabul kriteri:

```text
Migration temiz çalışır.
Mevcut document/upload akışı bozulmaz.
CandidateFact reviewStatus/publicationStatus/validityStatus alanlarını taşır.
```

### Task 2.2 — ValidationResult endpointleri

Endpointler:

```text
GET /facts/:id/validation-results
POST /facts/:id/validate
```

Kabul kriteri:

```text
Candidate fact validate edilebilir.
ValidationResult PostgreSQL'e yazılır.
UI için JSON checks döner.
```

### Task 2.3 — GraphPatch modeli ve endpointleri

Endpointler:

```text
GET /graph-patches
GET /graph-patches/:id
POST /facts/:id/create-patch
POST /graph-patches/:id/approve
POST /graph-patches/:id/reject
```

Kabul kriteri:

```text
CandidateFact doğrudan publish edilmez.
Önce GraphPatch oluşur.
Patch review edilebilir.
```

## 6. Faz 3 — FastAPI output genişletme

### Task 3.1 — Pydantic schema update

FastAPI şu modelleri döndürmeye hazır olmalı:

```text
EvidenceAtom
ExtractedFact
ExtractionWarning
ProcessDocumentResponse
```

Kabul kriteri:

```text
Response camelCase alias destekler.
Evidence atomlar atomId ve contentHash taşır.
ExtractedFact evidenceAtomIds taşır.
```

### Task 3.2 — Evidence atom generator polish

Kabul kriteri:

```text
PDF/TXT/MD için stabil atom ID üretilir.
qualityScore hesaplanır.
sectionPath ve location korunur.
```

### Task 3.3 — Fact extraction ontology-aware hale getir

Kabul kriteri:

```text
LLM prompt sadece allowed ontology subset kullanır.
Ontology dışı relation filtered veya validation warning olur.
LLM failure durumunda atoms dönmeye devam eder.
```

## 7. Faz 4 — Validation engine

### Task 4.1 — Validation service iskeleti

Kontroller:

```text
schema
ontology
evidence support
temporal
source authority
conflict
ACL placeholder
business rules
```

Kabul kriteri:

```text
ValidationService candidate fact alır ve ValidationResult döner.
```

### Task 4.2 — Role cardinality conflict

Amaç: Ayşe/Mehmet örneği gibi ezilen bilgi senaryosunu desteklemek.

Kabul kriteri:

```text
SalesPresident için maxActiveHolders=1 kontrol edilir.
Mevcut active assertion varsa conflict veya role_transition patch önerilir.
```

## 8. Faz 5 — Graph patch publish

### Task 5.1 — GraphPatchService

Amaç: CandidateFact'ten GraphPatch üretmek.

Kabul kriteri:

```text
ADD_ASSERTION operation desteklenir.
EXPIRE_ASSERTION operation desteklenir.
Evidence refs patch içinde taşınır.
```

### Task 5.2 — Publish endpoint'i patch bazlı hale getir

Endpoint:

```text
POST /graph-patches/:id/publish
```

Kabul kriteri:

```text
Sadece approved patch publish edilir.
Candidate/rejected patch publish edilemez.
Neo4j idempotent MERGE kullanır.
PublishedAssertion kayıtları oluşur.
```

## 9. Faz 6 — Semantic memory

### Task 6.1 — SemanticMemoryItem modeli ve service

Amaç: Curated KG'den öz bilgi kartı üretmek.

Kabul kriteri:

```text
Publish sonrası ilgili memory item invalidate/update edilir.
SemanticMemoryItem summary, currentFactRefs, evidenceAtomIds taşır.
```

### Task 6.2 — Memory endpointleri

Endpointler:

```text
GET /memory
GET /memory/:id
GET /entities/:id/memory
```

Kabul kriteri:

```text
Semantic memory card frontend'de gösterilebilir.
```

## 10. Faz 7 — Working memory ve Ask

### Task 7.1 — WorkingMemoryBuilder

Amaç: LLM/ask için küçük context paketi hazırlamak.

Kabul kriteri:

```text
Question/entity intent'e göre semantic memory + curated facts + evidence seçilir.
Tüm graph veya tüm archive LLM'e verilmez.
```

### Task 7.2 — Ask endpoint semantic-memory-first hale getir

Akış:

```text
Semantic Memory first
Curated KG fallback
Evidence retrieval
Source-grounded answer
```

Kabul kriteri:

```text
En az 5 soru evidence'lı cevap döner.
Cevap current vs historical ayrımını yapabilir.
```

## 11. Faz 8 — Frontend ekranları

### Task 8.1 — Validation result UI

Candidate fact detayında validation checks görünür.

### Task 8.2 — Graph patch review UI

Patch operations, evidence ve önerilen aksiyon görünür.

### Task 8.3 — Semantic memory UI

Memory card list/detail ekranı eklenir.

### Task 8.4 — Ask UI polish

Cevap yanında evidence, memory source ve approval bilgisi görünür.

## 12. Faz 9 — Smoke test ve polish

### Task 9.1 — Mock data güncelle

Ayşe/Mehmet role transition örneği, müşteri hedefi ve servis dependency örnekleri eklenir.

### Task 9.2 — Smoke test checklist uygula

`docs/smoke-test-checklist.md` takip edilir.

### Task 9.3 — README setup güncelle

Local setup, env, migration ve demo flow netleştirilir.

## 13. Önerilen commit grupları

Codex commit atmayacak. Kullanıcı manuel commit atacak.

```text
docs: restructure living memory documentation
refactor(ontology): add living memory ontology concepts
feat(api): add validation and graph patch models
feat(ai): align extraction contracts with ontology
feat(api): add validation engine
feat(api): add graph patch publish flow
feat(api): add semantic memory service
feat(web): add validation and patch review screens
feat(web): add semantic memory screens
feat(api): make ask semantic-memory-first
docs: add smoke test and setup updates
```

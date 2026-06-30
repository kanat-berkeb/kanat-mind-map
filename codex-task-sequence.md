# Codex Task Sequence — Kanat Mind Map Living Memory MVP

Bu doküman, `kanat-mind-map` projesini yeni evidence-first living memory mimarisine göre adım adım Codex ile geliştirmek için hazırlanmıştır.

Bu dosyadaki her task tek başına Codex’e verilebilir. Her taskta ilgili `docs/` dosyalarına referans verilir. Codex her taskta ayrıca root `AGENTS.md` dosyasındaki kurallara uymalıdır.

---

## 0. Çalışma yöntemi

Her task için önerilen kullanım:

```text
1. Task promptunu Codex’e ver.
2. Codex’in değiştirdiği dosyaları incele.
3. git diff ile kontrol et.
4. Gerekli build/test/migration komutlarını çalıştır.
5. Manuel smoke test yap.
6. Uygunsa commit’i sen at.
7. Sonraki taska geç.
```

Codex commit atmamalıdır.

Önerilen branch:

```bash
git checkout -b refactor/living-memory-architecture
```

---

## 1. Genel task prompt şablonu

Her taskta şu şablonu kullan:

```text
Bu repo kanat-mind-map projesidir.

Önce root AGENTS.md dosyasını oku ve oradaki kurallara uy.

Bu task için ayrıca şu dokümanları oku:
- docs/...

Amaç:
...

Kapsam:
...

Yapılmayacaklar:
...

Kabul kriterleri:
...

Task sonunda:
- Değişen dosyaları listele.
- Çalıştırmam gereken komutları yaz.
- Manuel kontrol checklist'i yaz.
- Riskli veya eksik kalan noktaları belirt.
- Commit atma.
```

---

# FAZ 0 — Doküman ve ajan kuralları

---

## Task 0.1 — Yeni doküman setini repo’ya yerleştir

### İlgili dokümanlar

Bu taskta dış doküman referansı gerekmez. Dosyalar doğrudan repo’ya eklenecek.

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Amaç:
Yeni living memory doküman setini repo içine yerleştir.

Kapsam:
- Root README.md dosyasını güncelle veya mevcutsa koruyup yeni proje adını işle.
- docs/ klasörü altında aşağıdaki dosyaların varlığını doğrula veya oluştur:
  - project-overview.md
  - mvp-demo-plan.md
  - system-architecture.md
  - memory-taxonomy.md
  - evidence-atom-rules.md
  - fact-lifecycle.md
  - data-model-spec.md
  - ontology-governance.md
  - validation-review-policy.md
  - codex-task-plan.md
  - development-guidelines.md
  - smoke-test-checklist.md

Yapılmayacaklar:
- Kod değiştirme.
- package.json değiştirme.
- Docker veya env dosyalarını değiştirme.
- Commit atma.

Kabul kriterleri:
- docs/ klasörü düzenli olmalı.
- Doküman isimleri kebab-case olmalı.
- Root README.md projenin adını kanat-mind-map olarak göstermeli.
- Eski proje adı varsa sadece açıklama düzeyinde kalmalı, ana ad kanat-mind-map olmalı.

Task sonunda değişen dosyaları ve kontrol adımlarını yaz.
```

---

## Task 0.2 — AGENTS.md dosyasını ekle

### İlgili dokümanlar

- `docs/system-architecture.md`
- `docs/memory-taxonomy.md`
- `docs/fact-lifecycle.md`
- `docs/validation-review-policy.md`
- `docs/development-guidelines.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şu dokümanları oku:
- docs/system-architecture.md
- docs/memory-taxonomy.md
- docs/fact-lifecycle.md
- docs/validation-review-policy.md
- docs/development-guidelines.md

Amaç:
Root AGENTS.md dosyasını oluştur. Bu dosya Codex'in her taskta uyması gereken genel kuralları içerecek.

AGENTS.md içinde mutlaka şu kurallar olsun:
- apps/web yalnızca apps/api ile konuşur.
- apps/api PostgreSQL, Neo4j ve workflow state sahibidir.
- apps/ai-api stateless kalır; PostgreSQL veya Neo4j'ye yazmaz.
- LLM output truth değildir, candidate knowledge’dır.
- Candidate fact doğrudan Neo4j’ye publish edilmez.
- Curated KG yalnızca validation + review + graph patch ile güncellenir.
- Semantic Memory doğrudan LLM çıktısından değil Curated KG’den türetilir.
- Evidence atom memory değildir, kanıttır.
- Her task sonunda değişen dosyalar, kontrol komutları ve riskler raporlanır.
- Commit atılmaz.

Yapılmayacaklar:
- Kod değiştirme.
- Yeni dependency ekleme.
- Commit atma.

Kabul kriterleri:
- Root AGENTS.md oluşmalı.
- Kurallar açık ve uygulanabilir olmalı.
- Mevcut docs içeriğiyle çelişmemeli.
```

---

## Task 0.3 — Mevcut repo durum analizi

### İlgili dokümanlar

- `AGENTS.md`
- `docs/project-overview.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`
- `docs/codex-task-plan.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/project-overview.md
- docs/system-architecture.md
- docs/data-model-spec.md
- docs/codex-task-plan.md

Amaç:
Kod değiştirmeden mevcut repo durumunu analiz et.

Bana şunları raporla:
1. apps/web, apps/api, apps/ai-api mevcut mu?
2. Docker Compose içinde hangi servisler var?
3. Prisma schema mevcut mu, hangi modeller var?
4. FastAPI schema/endpointleri mevcut mu?
5. Next.js ekranları mevcut mu?
6. Yeni living memory mimarisine göre eksik ilk 10 teknik parça nedir?
7. Hangi tasktan başlamak en mantıklı?

Yapılmayacaklar:
- Kod değiştirme.
- Dosya oluşturma.
- Commit atma.

Kabul kriterleri:
- Sadece analiz raporu verilmeli.
- Tahmin ile kesin bilgi ayrılmalı.
```

---

# FAZ 1 — Ontology ve contracts

---

## Task 1.1 — Demo ontology dosyasını yeni mimariye göre güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/ontology-governance.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/ontology-governance.md
- docs/system-architecture.md
- docs/data-model-spec.md

Amaç:
packages/ontology/demo-ontology.yaml dosyasını living memory MVP yapısına göre güncelle.

Kapsam:
- Mevcut entity ve relation tiplerini koru.
- Şu entity tipleri yoksa ekle:
  Customer, Person, Team, Region, Product, Project, Service, Risk, SalesTarget, Decision, Document,
  EvidenceAtom, Role, RoleAssignment, Department, GraphPatch, SemanticMemoryItem, Conflict
- Relation tipleri için from/to, description, evidenceRequired, approvalRequired alanlarını tanımla.
- RoleAssignment ve SalesTarget gibi değişebilir bilgiler için temporalRequired: true benzeri kural ekle.
- Source authority ve review policy alanları için YAML yapısı hazırla.
- ontologyVersion alanı ekle.

Yapılmayacaklar:
- Backend kodu yazma.
- FastAPI promptunu değiştirme.
- Migration oluşturma.
- Commit atma.

Kabul kriterleri:
- YAML parse edilebilir olmalı.
- Her relation from/to kuralı taşımalı.
- LLM’in relation/entity uydurmaması için allowed list açık olmalı.
- MVP kapsamı ile future alanlar yorum veya metadata olarak ayrılmalı.
```

---

## Task 1.2 — Contracts dosyalarını oluştur veya genişlet

### İlgili dokümanlar

- `AGENTS.md`
- `docs/data-model-spec.md`
- `docs/evidence-atom-rules.md`
- `docs/validation-review-policy.md`
- `docs/fact-lifecycle.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/data-model-spec.md
- docs/evidence-atom-rules.md
- docs/validation-review-policy.md
- docs/fact-lifecycle.md

Amaç:
packages/contracts altında servis sınırlarında kullanılacak JSON schema veya TypeScript type contract dosyalarını oluştur/güncelle.

Kapsam:
Şu contract dosyalarını oluştur veya mevcutları genişlet:
- evidence-atom.schema.json
- candidate-fact.schema.json
- validation-result.schema.json
- graph-patch.schema.json
- published-assertion.schema.json
- semantic-memory-item.schema.json
- process-document-response.schema.json

Alan adları API contract tarafında camelCase olsun.

Yapılmayacaklar:
- Prisma schema değiştirme.
- Backend controller yazma.
- FastAPI kodu değiştirme.
- Commit atma.

Kabul kriterleri:
- EvidenceAtom contract docs/evidence-atom-rules.md ile uyumlu olmalı.
- CandidateFact reviewStatus/publicationStatus/validityStatus alanlarını desteklemeli.
- GraphPatch operation listesi içermeli.
- SemanticMemoryItem evidenceRefs, currentFacts, importantHistory, accessPolicy ve freshness bilgisi taşımalı.
```

---

# FAZ 2 — PostgreSQL data model

---

## Task 2.1 — Prisma status enumlarını ve temel lifecycle alanlarını ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/fact-lifecycle.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/fact-lifecycle.md
- docs/data-model-spec.md

Amaç:
Prisma schema’da fact lifecycle için gerekli enumları ve temel alanları ekle.

Kapsam:
- ReviewStatus enum:
  candidate, validated, needs_review, approved, rejected
- PublicationStatus enum:
  unpublished, published, publish_failed
- ValidityStatus enum:
  active, expired, superseded, retracted, conflicted
- Mevcut CandidateFact modelinde mümkünse geriye uyumlu şekilde:
  reviewStatus
  publicationStatus
  validityStatus
  ontologyVersion
  validationSummary
  accessPolicy
  validFrom
  validUntil
  knownFrom
  knownUntil
alanlarını ekle.

Yapılmayacaklar:
- Endpoint yazma.
- FastAPI değiştirme.
- Frontend değiştirme.
- Neo4j logic değiştirme.
- Commit atma.

Kabul kriterleri:
- npx prisma validate başarılı olmalı.
- Mevcut status alanı varsa kırmadan migration planı oluşturulmalı.
- Yeni alanlar nullable/default değerlerle mevcut veriyi bozmayacak şekilde eklenmeli.
```

---

## Task 2.2 — ValidationResult ve ReviewDecision modellerini ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`
- `docs/fact-lifecycle.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/validation-review-policy.md
- docs/data-model-spec.md
- docs/fact-lifecycle.md

Amaç:
Prisma schema’ya ValidationResult ve ReviewDecision modellerini ekle.

Kapsam:
ValidationResult:
- id
- candidateFactId
- overallStatus
- severity
- checks Json
- recommendedAction
- createdAt

ReviewDecision:
- id
- candidateFactId
- reviewerId nullable
- decision
- reason nullable
- changedFields Json nullable
- createdAt

İlişkiler CandidateFact ile kurulmalı.

Yapılmayacaklar:
- Controller yazma.
- UI yazma.
- Commit atma.

Kabul kriterleri:
- Prisma schema valid olmalı.
- CandidateFact ile relation kurulmalı.
- Bir candidate fact birden fazla validation result ve review decision taşıyabilmeli.
```

---

## Task 2.3 — ConflictRecord, GraphPatch, PublishedAssertion ve SemanticMemoryItem modellerini ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/data-model-spec.md`
- `docs/memory-taxonomy.md`
- `docs/fact-lifecycle.md`
- `docs/validation-review-policy.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/data-model-spec.md
- docs/memory-taxonomy.md
- docs/fact-lifecycle.md
- docs/validation-review-policy.md

Amaç:
Yeni living memory mimarisi için PostgreSQL workflow modellerini ekle.

Kapsam:
Prisma schema’ya şu modelleri ekle:
- ConflictRecord
- GraphPatch
- PublishedAssertion
- SemanticMemoryItem

GraphPatch:
- patchType
- operations Json
- validationResultId nullable
- reviewStatus
- publicationStatus
- createdAt
- appliedAt nullable

PublishedAssertion:
- subjectType, subjectName
- predicate
- objectType, objectName
- objectProperties Json nullable
- evidenceAtomIds Json
- sourceDocumentId nullable
- graphPatchId nullable
- validityStatus
- validFrom, validUntil
- accessPolicy
- createdAt, updatedAt

SemanticMemoryItem:
- memoryType
- subjectType, subjectName
- summary
- currentFacts Json
- importantHistory Json nullable
- evidenceRefs Json
- accessPolicy
- freshnessStatus
- lastVerifiedAt nullable
- generatedFrom
- createdAt, updatedAt

Yapılmayacaklar:
- Service/controller yazma.
- Neo4j publish değiştirme.
- Commit atma.

Kabul kriterleri:
- npx prisma validate başarılı olmalı.
- Modeller docs/data-model-spec.md ile uyumlu olmalı.
- SemanticMemoryItem candidate fact’e değil PublishedAssertion/Curated KG mantığına göre tasarlanmalı.
```

---

# FAZ 3 — FastAPI schema ve extraction contract uyumu

---

## Task 3.1 — FastAPI response schema’larını contracts ile uyumlu hale getir

### İlgili dokümanlar

- `AGENTS.md`
- `docs/evidence-atom-rules.md`
- `docs/data-model-spec.md`
- `docs/validation-review-policy.md`
- `packages/contracts/process-document-response.schema.json`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/evidence-atom-rules.md
- docs/data-model-spec.md
- docs/validation-review-policy.md
- packages/contracts/process-document-response.schema.json

Amaç:
apps/ai-api Pydantic schema’larını yeni contract yapısına uyumlu hale getir.

Kapsam:
- EvidenceAtom schema’sı camelCase API alanlarıyla uyumlu olsun.
- ExtractedFact / CandidateFact response:
  subjectName, subjectType, predicate, objectName, objectType, objectProperties,
  evidenceAtomIds, evidenceText, llmConfidence, approvalScore,
  validFrom, validUntil, ontologyVersion, extractionWarnings
alanlarını desteklesin.
- ProcessDocumentResponse metadata/warnings alanı taşıyabilsin.

Yapılmayacaklar:
- PostgreSQL veya Neo4j bağlantısı ekleme.
- NestJS değiştirme.
- Frontend değiştirme.
- Commit atma.

Kabul kriterleri:
- FastAPI OpenAPI docs schema’ları göstermeli.
- apps/ai-api stateless kalmalı.
- LLM hata verirse evidence atoms dönebilmeli, candidate facts boş dönebilmeli.
```

---

## Task 3.2 — Evidence atom generator’ı yeni kurallara göre sıkılaştır

### İlgili dokümanlar

- `AGENTS.md`
- `docs/evidence-atom-rules.md`
- `docs/memory-taxonomy.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/evidence-atom-rules.md
- docs/memory-taxonomy.md

Amaç:
apps/ai-api evidence atom generator servisinin docs/evidence-atom-rules.md ile uyumunu artır.

Kapsam:
- Stabil atomId üretimi.
- atomIndex deterministik olsun.
- sourceType, pageNumber, sectionPath, charStart, charEnd, qualityScore, metadata alanları düzgün üretilebilsin.
- 1500 karakter üzeri atomları cümle/kelime sınırından böl.
- 80 karakter altı bağlamsız parçaları mümkünse birleştir.
- Markdown heading sectionPath korunsun.
- Transcript speaker metadata korunsun.

Yapılmayacaklar:
- LLM extraction değiştirme.
- NestJS değiştirme.
- Commit atma.

Kabul kriterleri:
- Aynı input aynı atomId dizisini üretmeli.
- Evidence atom metni yorum eklememeli.
- qualityScore approvalScore ile karıştırılmamalı.
```

---

## Task 3.3 — Fact extraction promptunu ontology-aware hale getir

### İlgili dokümanlar

- `AGENTS.md`
- `docs/ontology-governance.md`
- `docs/validation-review-policy.md`
- `packages/ontology/demo-ontology.yaml`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/ontology-governance.md
- docs/validation-review-policy.md
- packages/ontology/demo-ontology.yaml

Amaç:
apps/ai-api fact extraction service promptunu ontology-aware ve evidence-bound hale getir.

Kapsam:
- LLM’e sadece allowed entity/relation tipleri verilsin.
- LLM yeni entity/relation type uydurmasın.
- Her fact için evidenceAtomIds zorunlu olsun.
- evidenceText source atomlarla uyumlu quote/özet olmalı.
- llmConfidence 0-1 aralığında olmalı.
- approvalScore NestJS tarafında veya FastAPI tarafında deterministic hesaplanmalı.
- validFrom/validUntil çıkarılabiliyorsa dolsun.
- Çıkarılamayan temporal bilgi nullable kalsın.

Yapılmayacaklar:
- apps/ai-api DB’ye yazmasın.
- Neo4j logic ekleme.
- Commit atma.

Kabul kriterleri:
- Ontology dışı fact’ler response’ta validation warning ile işaretlenebilmeli veya filtrelenmeli.
- Prompt kaynakta olmayan bilgi çıkarma yasağını açıkça içermeli.
```

---

# FAZ 4 — NestJS extraction ve persistence

---

## Task 4.1 — NestJS extract endpoint’ini yeni response contract’a uyarla

### İlgili dokümanlar

- `AGENTS.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`
- `docs/evidence-atom-rules.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/system-architecture.md
- docs/data-model-spec.md
- docs/evidence-atom-rules.md

Amaç:
POST /documents/:id/extract endpoint’ini FastAPI’nin yeni ProcessDocumentResponse contract’ına uyumlu hale getir.

Kapsam:
- Evidence atoms PostgreSQL’e yazılsın.
- Candidate facts PostgreSQL’e yazılsın.
- Candidate facts başlangıçta:
  reviewStatus = candidate
  publicationStatus = unpublished
  validityStatus = active veya nullable/default
olarak set edilsin.
- FastAPI warnings varsa document metadata veya extraction log alanında saklanabilsin.
- Document status extracted/failed doğru güncellensin.

Yapılmayacaklar:
- Validation engine’i bu taskta yazma.
- Review endpointlerini değiştirme.
- Neo4j publish değiştirme.
- Commit atma.

Kabul kriterleri:
- FastAPI response alanları doğru map edilmeli.
- apps/api veri sahibi olmaya devam etmeli.
- apps/ai-api DB’ye yazmamalı.
```

---

## Task 4.2 — Documents detail için facts endpoint uyumu

### İlgili dokümanlar

- `AGENTS.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/system-architecture.md
- docs/data-model-spec.md

Amaç:
Document detail ekranlarının kullanacağı backend endpointlerini yeni CandidateFact alanlarıyla uyumlu hale getir.

Kapsam:
- GET /documents/:id/facts endpoint’i yoksa ekle.
- Candidate facts response içinde reviewStatus, publicationStatus, validityStatus, validationSummary, evidenceAtomIds, evidenceText alanları dönsün.
- GET /documents/:id/evidence-atoms endpoint’i mevcut contract ile uyumlu olsun.

Yapılmayacaklar:
- Frontend değiştirme.
- Publish logic değiştirme.
- Commit atma.

Kabul kriterleri:
- Document detail için metadata + evidence atoms + candidate facts alınabilir olmalı.
```

---

# FAZ 5 — Validation Engine

---

## Task 5.1 — ValidationService skeleton ve check result formatı

### İlgili dokümanlar

- `AGENTS.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`
- `docs/fact-lifecycle.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/validation-review-policy.md
- docs/data-model-spec.md
- docs/fact-lifecycle.md

Amaç:
NestJS apps/api içinde ValidationService skeleton oluştur.

Kapsam:
- validateCandidateFact(candidateFactId) metodu olsun.
- ValidationResult formatı docs/validation-review-policy.md ile uyumlu olsun.
- İlk aşamada şu check’ler implement edilsin:
  schema_validation
  evidence_presence_validation
  confidence_range_validation
  temporal_basic_validation
- Check sonuçları ValidationResult tablosuna yazılsın.
- CandidateFact reviewStatus gerekirse validated veya needs_review yapılabilsin.

Yapılmayacaklar:
- Ontology validation detaylarını bu taskta tam yazma.
- Conflict detection yazma.
- UI yazma.
- Commit atma.

Kabul kriterleri:
- Bir candidate fact için validation result üretilebilmeli.
- Her check passed/failed/warning status taşımalı.
- ValidationResult persistent olmalı.
```

---

## Task 5.2 — Ontology validation ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/ontology-governance.md`
- `docs/validation-review-policy.md`
- `packages/ontology/demo-ontology.yaml`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/ontology-governance.md
- docs/validation-review-policy.md
- packages/ontology/demo-ontology.yaml

Amaç:
ValidationService içine ontology validation kontrollerini ekle.

Kapsam:
- subjectType allowed entity list içinde mi?
- objectType allowed entity list içinde mi?
- predicate allowed relation list içinde mi?
- predicate için subject/object type uyumlu mu?
- evidenceRequired relation için evidenceAtomIds var mı?
- temporalRequired relation için validFrom/validUntil veya period/objectProperties kontrolü yapılabiliyor mu?

Yapılmayacaklar:
- Ontology proposal sistemi yazma.
- FastAPI değiştirme.
- Commit atma.

Kabul kriterleri:
- Ontology dışı candidate fact validation failed veya needs_review olmalı.
- Check sonucu ValidationResult.checks içinde ayrıntılı görünmeli.
```

---

## Task 5.3 — Evidence support validation temelini ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/evidence-atom-rules.md`
- `docs/validation-review-policy.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/evidence-atom-rules.md
- docs/validation-review-policy.md

Amaç:
Candidate fact’in referans verdiği evidence atomların gerçekten var olduğunu ve evidenceText ile uyumlu olduğunu kontrol eden temel validation ekle.

Kapsam:
- evidenceAtomIds boşsa failed.
- Referans verilen atomlar PostgreSQL’de yoksa failed.
- evidenceText varsa atom textleri içinde en azından lexical overlap veya substring benzerliği kontrolü yap.
- Şimdilik gelişmiş NLI/LLM judge ekleme.
- Düşük uyumda warning/needs_review üret.

Yapılmayacaklar:
- Yeni LLM call ekleme.
- Frontend değiştirme.
- Commit atma.

Kabul kriterleri:
- Evidence atom varlığı kontrol ediliyor olmalı.
- Evidence text uyumsuzluğu validation result olarak görülebilmeli.
```

---

# FAZ 6 — Review ve conflict yönetimi

---

## Task 6.1 — ReviewDecision endpointlerini yeni lifecycle’a göre güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/fact-lifecycle.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/fact-lifecycle.md
- docs/validation-review-policy.md
- docs/data-model-spec.md

Amaç:
Approve/reject endpointlerini ReviewDecision kaydı üretecek şekilde güncelle.

Kapsam:
- POST /facts/:id/approve:
  ReviewDecision oluşturur.
  CandidateFact.reviewStatus = approved yapar.
- POST /facts/:id/reject:
  ReviewDecision oluşturur.
  CandidateFact.reviewStatus = rejected yapar.
  publicationStatus unpublished kalır.
- Optional reason body’den alınabilir.
- Eski status alanı varsa geriye uyum için güncellenebilir.

Yapılmayacaklar:
- Publish logic değiştirme.
- Frontend değiştirme.
- Commit atma.

Kabul kriterleri:
- Approve/reject kararları persistent olmalı.
- Review history kaybolmamalı.
```

---

## Task 6.2 — Conflict detection temelini ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/fact-lifecycle.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/fact-lifecycle.md
- docs/validation-review-policy.md
- docs/data-model-spec.md

Amaç:
Aynı subject + predicate + temporal scope için çelişkili active/published assertion veya approved candidate var mı kontrol eden temel ConflictDetectionService ekle.

Kapsam:
- CandidateFact için basic conflict scan metodu yaz.
- Aynı subjectName + predicate için farklı objectName varsa conflict candidate üret.
- ConflictRecord tablosuna kayıt at.
- CandidateFact.validityStatus = conflicted veya reviewStatus = needs_review yapılabilir.
- Source authority henüz basit tutulabilir.

Yapılmayacaklar:
- Otomatik conflict resolution yapma.
- Frontend conflict ekranı yazma.
- Commit atma.

Kabul kriterleri:
- Basit çelişki durumunda ConflictRecord oluşmalı.
- Conflict bilgisi validation/review akışında görülebilmeli.
```

---

# FAZ 7 — Graph Patch ve publish akışı

---

## Task 7.1 — GraphPatchService skeleton oluştur

### İlgili dokümanlar

- `AGENTS.md`
- `docs/data-model-spec.md`
- `docs/fact-lifecycle.md`
- `docs/system-architecture.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/data-model-spec.md
- docs/fact-lifecycle.md
- docs/system-architecture.md

Amaç:
CandidateFact’ten GraphPatch proposal üreten GraphPatchService skeleton oluştur.

Kapsam:
- createPatchFromCandidateFact(candidateFactId) metodu.
- Sadece reviewStatus=approved candidate fact için patch oluşturulabilsin.
- Patch operations Json içinde en az ADD_ASSERTION operasyonu olsun.
- GraphPatch.reviewStatus = approved veya needs_review policy’ye göre set edilsin.
- GraphPatch.publicationStatus = unpublished olsun.

Yapılmayacaklar:
- Neo4j’ye yazma.
- PublishedAssertion oluşturma.
- Frontend değiştirme.
- Commit atma.

Kabul kriterleri:
- Approved candidate fact için GraphPatch üretilebilmeli.
- Candidate/rejected fact için patch üretilememeli.
```

---

## Task 7.2 — Publish endpointini GraphPatch akışına taşı

### İlgili dokümanlar

- `AGENTS.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`
- `docs/fact-lifecycle.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/system-architecture.md
- docs/data-model-spec.md
- docs/fact-lifecycle.md

Amaç:
Mevcut fact publish akışını CandidateFact -> GraphPatch -> Neo4j/PublishedAssertion mantığına yaklaştır.

Kapsam:
- Mevcut POST /facts/:id/publish endpoint’i geriye uyum için kalabilir.
- Endpoint önce approved CandidateFact için GraphPatch oluşturmalı veya mevcut patch’i bulmalı.
- GraphPatch operations uygulanarak Neo4j MERGE yapılmalı.
- Başarılı publish sonrası PublishedAssertion kaydı oluşturulmalı.
- CandidateFact.publicationStatus = published yapılmalı.
- GraphPatch.publicationStatus = published ve appliedAt set edilmeli.

Yapılmayacaklar:
- Complex expire/supersede logic yazma.
- Semantic memory builder’ı bu taskta yazma.
- Commit atma.

Kabul kriterleri:
- Candidate/rejected fact publish edilemez.
- Approved fact publish edildiğinde Neo4j ve PostgreSQL PublishedAssertion tutarlı olmalı.
- Publish idempotent olmalı.
```

---

## Task 7.3 — Expire/supersede operasyonları için temel destek ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/fact-lifecycle.md`
- `docs/data-model-spec.md`
- `docs/validation-review-policy.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/fact-lifecycle.md
- docs/data-model-spec.md
- docs/validation-review-policy.md

Amaç:
GraphPatch operations içinde EXPIRE_ASSERTION ve SUPERSEDE_ASSERTION operasyonlarını temel seviyede destekle.

Kapsam:
- PublishedAssertion validityStatus active/expired/superseded güncellenebilsin.
- validUntil set edilebilsin.
- supersededBy veya metadata içinde replacement assertion referansı tutulabilsin.
- RoleAssignment/SalesPresident gibi tek aktif holder kurallarına hazırlık yapılabilsin.

Yapılmayacaklar:
- Tam otomatik role transition agent yazma.
- UI değiştirme.
- Commit atma.

Kabul kriterleri:
- Eski bilgi silinmeden expired/superseded yapılabiliyor olmalı.
- Historical bilgi korunmalı.
```

---

# FAZ 8 — Semantic Memory

---

## Task 8.1 — SemanticMemoryService skeleton oluştur

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/data-model-spec.md`
- `docs/system-architecture.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/data-model-spec.md
- docs/system-architecture.md

Amaç:
Curated KG / PublishedAssertion kayıtlarından SemanticMemoryItem üreten SemanticMemoryService skeleton oluştur.

Kapsam:
- rebuildMemoryForSubject(subjectType, subjectName) metodu.
- Subject’e ait active PublishedAssertion kayıtlarını toplasın.
- summary basit template ile üretilebilir.
- currentFacts Json doldurulsun.
- importantHistory expired/superseded assertionlardan doldurulabilir.
- evidenceRefs birleştirilsin.
- accessPolicy en kısıtlayıcı kaynak politikasından türetilsin veya MVP’de conservative default kullanılsın.

Yapılmayacaklar:
- LLM summary kullanma.
- Candidate facts üzerinden memory üretme.
- Frontend değiştirme.
- Commit atma.

Kabul kriterleri:
- SemanticMemoryItem doğrudan candidate fact’ten değil PublishedAssertion’dan üretilmeli.
- Memory item evidenceRefs ve accessPolicy taşımalı.
```

---

## Task 8.2 — Publish sonrası semantic memory refresh ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/system-architecture.md
- docs/data-model-spec.md

Amaç:
GraphPatch publish başarılı olduktan sonra ilgili subject için SemanticMemoryItem refresh edilmesini sağla.

Kapsam:
- Publish akışı sonunda SemanticMemoryService.rebuildMemoryForSubject çağrılabilir.
- Hata olursa publish işlemi rollback edilmesin; memory refresh hatası loglanıp raporlanabilir.
- SemanticMemoryItem updatedAt değişmeli.

Yapılmayacaklar:
- Event bus ekleme.
- Queue ekleme.
- Commit atma.

Kabul kriterleri:
- Publish sonrası ilgili entity için semantic memory güncellenmeli.
- Semantic memory refresh candidate/rejected fact için çalışmamalı.
```

---

## Task 8.3 — Semantic memory API endpointleri

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/data-model-spec.md

Amaç:
SemanticMemoryItem kayıtlarını okumak için API endpointleri ekle.

Endpointler:
- GET /memory
- GET /memory/:id
- POST /memory/rebuild

Kapsam:
- GET /memory subjectType, subjectName, memoryType filtrelerini destekleyebilir.
- POST /memory/rebuild body ile subjectType ve subjectName alabilir.
- ACL enforcement MVP’de placeholder olabilir ama accessPolicy response’ta dönmeli.

Yapılmayacaklar:
- Frontend yazma.
- LLM summary ekleme.
- Commit atma.

Kabul kriterleri:
- Semantic memory listelenebilir ve rebuild edilebilir olmalı.
```

---

# FAZ 9 — Ask / Working Memory

---

## Task 9.1 — WorkingMemoryBuilder oluştur

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/system-architecture.md
- docs/data-model-spec.md

Amaç:
Ask veya agent çağrıları için küçük, task-specific context pack üreten WorkingMemoryBuilder oluştur.

Kapsam:
- buildForAskQuestion(question) metodu.
- Basit entity extraction ile subjectName tahmini yapılabilir.
- SemanticMemoryItem varsa context pack’e eklenir.
- Gerekirse PublishedAssertion ve evidenceRefs eklenir.
- Tüm graph veya tüm memory LLM’e verilmez.

Yapılmayacaklar:
- Genel amaçlı RAG framework ekleme.
- Vector DB ekleme.
- Commit atma.

Kabul kriterleri:
- Working memory çıktısı küçük ve açıklanabilir olmalı.
- Semantic Memory first yaklaşımı uygulanmalı.
```

---

## Task 9.2 — Ask endpointini Semantic Memory first hale getir

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/system-architecture.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/system-architecture.md
- docs/data-model-spec.md

Amaç:
POST /ask endpoint’ini önce Semantic Memory, sonra Curated KG/Neo4j fallback kullanacak şekilde güncelle.

Kapsam:
- Basic intent parser korunabilir.
- Soru desteklenen intent ise önce SemanticMemoryItem aranır.
- Memory yeterliyse cevap memory + evidenceRefs ile döner.
- Memory yoksa Neo4j template query fallback çalışabilir.
- Response içinde answer, matches, evidenceRefs, sourceType alanları olsun.

Yapılmayacaklar:
- Serbest LLM Cypher generation ekleme.
- Vector search ekleme.
- Commit atma.

Kabul kriterleri:
- Ask cevabı candidate fact’lerden değil Semantic Memory / PublishedAssertion / Neo4j’den gelmeli.
- Evidence bilgisi korunmalı.
```

---

# FAZ 10 — Frontend

---

## Task 10.1 — Candidate facts ekranını lifecycle alanlarıyla güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/fact-lifecycle.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/fact-lifecycle.md
- docs/validation-review-policy.md
- docs/data-model-spec.md

Amaç:
apps/web /facts ekranını yeni lifecycle alanlarıyla uyumlu hale getir.

Kapsam:
- reviewStatus, publicationStatus, validityStatus sütunları gösterilsin.
- Eski status varsa geriye uyumlu gösterim yapılabilir.
- Evidence text, approvalScore, llmConfidence görünmeye devam etsin.
- Approve/reject butonları yeni endpoint davranışına uygun çalışsın.

Yapılmayacaklar:
- Graph viewer değiştirme.
- Ask ekranı değiştirme.
- Commit atma.

Kabul kriterleri:
- Kullanıcı candidate/approved/rejected/published ayrımını görebilmeli.
```

---

## Task 10.2 — Validation result detail UI ekle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/validation-review-policy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/validation-review-policy.md
- docs/data-model-spec.md

Amaç:
Fact detail dialog/drawer içinde validation result detaylarını göster.

Kapsam:
- Validation checks listesi gösterilsin.
- passed/failed/warning durumları badge ile ayrılabilir.
- recommendedAction görünür olsun.
- Validation result yoksa empty state gösterilsin.
- Gerekirse GET /facts/:id endpoint’i validationResults include edecek şekilde backend de güncellenebilir.

Yapılmayacaklar:
- Yeni validation logic yazma.
- Commit atma.

Kabul kriterleri:
- Reviewer candidate fact’in neden needs_review olduğunu görebilmeli.
```

---

## Task 10.3 — Graph patch review/list ekranı

### İlgili dokümanlar

- `AGENTS.md`
- `docs/data-model-spec.md`
- `docs/fact-lifecycle.md`
- `docs/system-architecture.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/data-model-spec.md
- docs/fact-lifecycle.md
- docs/system-architecture.md

Amaç:
GraphPatch kayıtlarını görmek ve publish aksiyonunu tetiklemek için basit frontend ekranı ekle.

Route:
- /patches

Kapsam:
- GraphPatch listesi.
- patchType, reviewStatus, publicationStatus, createdAt, appliedAt göster.
- Operations JSON okunabilir formatta göster.
- Approved/unpublished patch için publish butonu.
- Backend endpointleri yoksa minimal GET /patches ve POST /patches/:id/publish eklenebilir.

Yapılmayacaklar:
- Complex visual diff UI yapma.
- Commit atma.

Kabul kriterleri:
- Kullanıcı graph patch’in ne değiştireceğini publish öncesi görebilmeli.
```

---

## Task 10.4 — Semantic memory ekranı

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/data-model-spec.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/data-model-spec.md

Amaç:
SemanticMemoryItem kayıtlarını listeleyen ve detayını gösteren basit frontend ekranı ekle.

Route:
- /memory

Kapsam:
- subjectType, subjectName, memoryType, freshnessStatus, updatedAt listelensin.
- Detayda summary, currentFacts, importantHistory, evidenceRefs, accessPolicy gösterilsin.
- Rebuild action opsiyonel buton olarak eklenebilir.

Yapılmayacaklar:
- LLM summary edit UI yapma.
- Commit atma.

Kabul kriterleri:
- Kullanıcı Curated KG’den türetilmiş öz memory kartlarını görebilmeli.
```

---

## Task 10.5 — Ask ekranını evidence/memory source gösterecek şekilde güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/memory-taxonomy.md`
- `docs/system-architecture.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/memory-taxonomy.md
- docs/system-architecture.md

Amaç:
apps/web /ask ekranında cevabın Semantic Memory’den mi Curated KG fallback’inden mi geldiğini göster.

Kapsam:
- Response sourceType gösterilsin:
  semantic_memory
  curated_kg
  unsupported
- Evidence refs/matches listesi gösterilsin.
- Unsupported soru için desteklenen örnekler korunmalı.
- Loading/error/empty state iyileştirilsin.

Yapılmayacaklar:
- Serbest LLM chat ekleme.
- Commit atma.

Kabul kriterleri:
- Kullanıcı cevabın kaynağını görebilmeli.
```

---

# FAZ 11 — Seed, smoke test ve dokümantasyon

---

## Task 11.1 — Mock data ve expected outputs düzenle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/mvp-demo-plan.md`
- `docs/evidence-atom-rules.md`
- `docs/smoke-test-checklist.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/mvp-demo-plan.md
- docs/evidence-atom-rules.md
- docs/smoke-test-checklist.md

Amaç:
Mock data klasörünü living memory MVP akışını gösterecek şekilde düzenle.

Kapsam:
- En az bir HR/organization role change örneği.
- En az bir sales customer target örneği.
- En az bir software service ownership/dependency örneği.
- expected/ klasöründe beklenen evidence atoms ve candidate facts örnekleri.
- README içinde mock data kullanım açıklaması.

Yapılmayacaklar:
- Parser logic değiştirme.
- Commit atma.

Kabul kriterleri:
- Demo role transition, customer target ve service dependency senaryolarını gösterebilmeli.
```

---

## Task 11.2 — README local setup ve demo flow güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/project-overview.md`
- `docs/mvp-demo-plan.md`
- `docs/system-architecture.md`
- `docs/smoke-test-checklist.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/project-overview.md
- docs/mvp-demo-plan.md
- docs/system-architecture.md
- docs/smoke-test-checklist.md

Amaç:
Root README.md dosyasını güncel living memory MVP akışına göre düzenle.

İçerik:
- Proje adı: kanat-mind-map
- Servisler: web, api, ai-api, postgres, neo4j
- Local setup
- Env dosyaları
- Prisma migration
- FastAPI çalıştırma
- Next.js çalıştırma
- Demo flow:
  1. Upload
  2. Extract
  3. Validation
  4. Review
  5. Graph Patch
  6. Publish
  7. Semantic Memory
  8. Ask
- Troubleshooting

Yapılmayacaklar:
- Kod değiştirme.
- Commit atma.

Kabul kriterleri:
- Yeni geliştirici README ile projeyi ayağa kaldırabilmeli.
```

---

## Task 11.3 — Smoke test checklist’i yeni akışa göre güncelle

### İlgili dokümanlar

- `AGENTS.md`
- `docs/smoke-test-checklist.md`
- `docs/mvp-demo-plan.md`
- `docs/system-architecture.md`

### Codex prompt

```text
Bu repo kanat-mind-map projesidir.

Önce şunları oku:
- AGENTS.md
- docs/smoke-test-checklist.md
- docs/mvp-demo-plan.md
- docs/system-architecture.md

Amaç:
docs/smoke-test-checklist.md dosyasını yeni akışa göre güncelle.

Checklist şunları kapsasın:
- Docker servisleri
- API health
- AI API health
- Web açılışı
- Upload
- Extract
- Evidence atoms
- Candidate facts
- Validation results
- Approve/reject
- Conflict detection temel senaryosu
- Graph patch creation
- Publish
- Neo4j graph
- PublishedAssertion
- SemanticMemoryItem
- Ask response
- Evidence/source display

Yapılmayacaklar:
- Kod değiştirme.
- Commit atma.

Kabul kriterleri:
- Demo öncesi uçtan uca manuel test listesi açık olmalı.
```

---

# 12. Önerilen commit grupları

Codex commit atmayacak. Commitleri kullanıcı manuel atacak.

Önerilen commit mesajları:

```text
docs: add living memory agent rules
docs: update project documentation for kanat mind map
feat(ontology): update demo ontology for living memory
feat(contracts): add living memory contracts
feat(api): add lifecycle status fields
feat(api): add validation and review models
feat(api): add graph patch and semantic memory models
feat(ai): align processing schemas with contracts
feat(api): integrate extraction with validation workflow
feat(api): add validation engine
feat(api): add conflict detection basics
feat(api): add graph patch workflow
feat(api): publish graph patches to curated graph
feat(api): add semantic memory builder
feat(api): make ask semantic memory first
feat(web): update candidate review screens
feat(web): add graph patch and memory screens
docs: update setup and smoke test checklist
```

---

# 13. Faz kalite kapıları

## Faz 1 sonunda

```text
Ontology ve contracts var.
LLM/entity/relation sınırları dokümante ve makine-okunur hale geldi.
```

## Faz 2 sonunda

```text
Prisma schema living memory workflow modellerini destekliyor.
```

## Faz 5 sonunda

```text
Candidate fact validation result üretebiliyor.
```

## Faz 7 sonunda

```text
Approved candidate fact GraphPatch üzerinden Curated KG’ye publish edilebiliyor.
```

## Faz 8 sonunda

```text
Publish sonrası SemanticMemoryItem oluşuyor.
```

## Faz 9 sonunda

```text
Ask endpoint candidate fact yerine semantic memory / curated KG üzerinden cevap veriyor.
```

## Faz 11 sonunda

```text
README ve smoke test checklist ile demo baştan sona çalıştırılabiliyor.
```

---

# 14. En önemli uyarı

Codex’e asla şu prompt verilmemeli:

```text
Tüm projeyi yeni mimariye geçir.
```

Doğru yaklaşım:

```text
Şu dokümanları oku.
Şu küçük taskı uygula.
Şu dosyalar dışında değişiklik yapma.
Şu kabul kriterlerini sağla.
Commit atma.
```

Bu proje büyüdükçe kontrolü korumanın en iyi yolu budur.

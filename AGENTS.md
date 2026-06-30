# AGENTS.md — Kanat Mind Map Codex Çalışma Kuralları

Bu dosya, `kanat-mind-map` reposunda Codex veya benzeri kod ajanlarıyla çalışırken her task için uygulanacak genel kuralları tanımlar.

Bu proje basit bir “PDF yükle, LLM fact çıkarsın, Neo4j’ye yaz” demosu değildir. Proje; evidence-first, human-curated, ontology-governed, semantic-memory-backed bir knowledge graph MVP’sidir.

---

## 1. Temel proje ilkesi

Sistemin ana bilgi akışı şudur:

```text
Raw Source
→ Evidence Archive
→ Evidence Atom
→ Candidate Knowledge
→ Validation
→ Human Review
→ Graph Patch
→ Curated Knowledge Graph
→ Semantic Memory
→ Working Memory
→ Ask / Agent Runtime
```

Bu akış bozulmamalıdır.

En önemli kural:

```text
LLM truth üretmez.
LLM candidate üretir.

Curated KG yalnızca validation + review + graph patch akışıyla güncellenir.
Semantic Memory doğrudan LLM çıktısından değil, Curated KG’den türetilir.
```

---

## 2. Değişmez servis sınırları

### `apps/web`

Next.js frontend uygulamasıdır.

Kurallar:

```text
apps/web yalnızca apps/api ile HTTP üzerinden konuşur.
apps/web doğrudan apps/ai-api ile konuşmaz.
apps/web doğrudan PostgreSQL, Neo4j veya dosya sistemine erişmez.
```

### `apps/api`

NestJS ana sistem sınırıdır.

Sorumlulukları:

```text
PostgreSQL persistence
Neo4j publish/query
workflow state
document upload
extraction orchestration
validation result persistence
human review
graph patch workflow
semantic memory builder orchestration
ask endpoint
```

Kurallar:

```text
apps/api veri sahibidir.
apps/api, apps/ai-api ile HTTP üzerinden konuşur.
apps/api, FastAPI response’unu doğrulamadan kalıcı hale getirmez.
apps/api, LLM çıktısını doğrudan Neo4j’ye yazmaz.
```

### `apps/ai-api`

FastAPI document/LLM servisidir.

Sorumlulukları:

```text
document parsing
evidence atom generation
LLM candidate extraction
structured JSON response
```

Kurallar:

```text
apps/ai-api stateless kalmalıdır.
apps/ai-api PostgreSQL’e yazmaz.
apps/ai-api Neo4j’ye yazmaz.
apps/ai-api başka uygulamaların internal dosyalarını import etmez.
```

---

## 3. Katman ayrımları

Aşağıdaki kavramlar karıştırılmamalıdır.

### Evidence Archive

Ham kaynakları, parsed document çıktıları ve evidence atomları saklar.

```text
Archive her şeyi saklar.
Archive truth değildir.
```

### Retrieval Substrate

Arama ve retrieval altyapısıdır.

```text
Lexical search
metadata filter
basic text search
future vector search
future OpenSearch
```

Retrieval index memory değildir.

### Candidate Knowledge Layer

LLM/agent tarafından çıkarılan aday bilgileri tutar.

```text
CandidateEntity
CandidateFact
CandidateClaim
CandidateConflict
GraphPatchProposal
OntologyProposal
```

Candidate bilgi resmi gerçek değildir.

### Curated Knowledge Graph

Onaylı, kanıtlı, validation’dan geçmiş structured bilgi grafıdır.

```text
Only approved graph patches update Curated KG.
Rejected/candidate facts never update Curated KG.
```

### Semantic Memory

Asıl “memory” katmanıdır.

Semantic Memory:

```text
Curated KG’den türetilir.
Öz, güncel, kanıta bağlı bilgi kartlarıdır.
LLM summary değildir.
Raw evidence değildir.
Vector DB değildir.
```

### Working Memory

LLM veya agent’in tek bir görev için gördüğü küçük context paketidir.

```text
Working Memory = task-specific context pack.
Tüm memory veya tüm graph LLM’e verilmez.
```

---

## 4. Status modeli

Tam mimaride tek `status` alanı yerine üç ayrı eksen tercih edilir:

```text
reviewStatus
publicationStatus
validityStatus
```

### `reviewStatus`

```text
candidate
validated
needs_review
approved
rejected
```

### `publicationStatus`

```text
unpublished
published
publish_failed
```

### `validityStatus`

```text
active
expired
superseded
retracted
conflicted
```

MVP’de tek `status` alanı varsa, yeni kod yazarken bu üç eksene geçişi kolaylaştıracak şekilde tasarım yapılmalıdır.

---

## 5. Evidence kuralları

Her candidate fact en az bir evidence atom referansı taşımalıdır.

Kurallar:

```text
evidenceAtomIds boş olamaz.
evidenceText kaynak atomlarla uyumlu olmalıdır.
LLM evidence uyduramaz.
Evidence atom metni extraction sonrasında keyfi değiştirilemez.
Evidence atomlar doğrudan Neo4j publish tetiklemez.
```

Evidence atom memory değildir. Evidence atom kanıttır.

---

## 6. Ontology kuralları

Ontology sistemin sözleşmesidir.

Kurallar:

```text
LLM yeni entity type uyduramaz.
LLM yeni relation type uyduramaz.
Candidate facts ontology’ye göre validate edilir.
Ontology değişiklikleri versioned olmalıdır.
Ontology agent tarafından doğrudan değiştirilmez.
Agent yalnızca ontology proposal üretebilir.
```

MVP’de `packages/ontology/demo-ontology.yaml` manuel yönetilebilir. Tam mimaride ontology governance sürecine geçilmelidir.

---

## 7. Validation kuralları

Candidate bilgi Curated KG’ye girmeden önce validation’dan geçmelidir.

Beklenen validation kontrolleri:

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

Validation sonucu persisted olmalıdır. Sadece runtime log olarak kalmamalıdır.

---

## 8. Human review kuralları

Kritik bilgiler insan onayına gitmelidir.

Özellikle:

```text
sales target
role assignment
price / discount
financial risk
legal claim
customer risk
product technical claim
ontology change
conflict resolution
```

Review kararı kayıt altına alınmalıdır.

```text
reviewer
decision
reason
createdAt
changedFields
```

---

## 9. Graph Patch kuralları

Curated KG doğrudan candidate fact üzerinden güncellenmemelidir.

Doğru akış:

```text
CandidateFact
→ ValidationResult
→ ReviewDecision
→ GraphPatch
→ PublishedAssertion / Neo4j update
→ SemanticMemoryItem refresh
```

Graph Patch operasyonları açık olmalıdır:

```text
ADD_NODE
ADD_ASSERTION
EXPIRE_ASSERTION
SUPERSEDE_ASSERTION
RETRACT_ASSERTION
MARK_CONFLICTED
UPDATE_ASSERTION_METADATA
```

---

## 10. Semantic Memory kuralları

Semantic Memory sadece güvenilir kaynaklardan üretilmelidir.

Kurallar:

```text
SemanticMemoryItem raw evidence’tan doğrudan oluşmaz.
SemanticMemoryItem candidate fact’ten doğrudan oluşmaz.
SemanticMemoryItem Curated KG / PublishedAssertion temelinden üretilir.
Memory item evidenceRefs taşır.
Memory item accessPolicy taşır.
Memory item freshness bilgisi taşır.
```

LLM summary memory’ye direkt yazılamaz. LLM summary en fazla candidate memory proposal olabilir.

---

## 11. ACL ve güvenlik kuralları

Türetilmiş bilgi, kaynağından daha geniş erişime sahip olamaz.

ACL şu katmanlarda taşınmalıdır:

```text
Raw source
Evidence atom
Candidate fact
Validation result
Graph patch
Published assertion
Semantic memory item
Ask response
```

Gizli source’dan gelen bilgi public memory item’a dönüşmemelidir.

---

## 12. Kod değiştirme kuralları

Her task küçük kapsamlı olmalıdır.

Codex şunları yapmamalıdır:

```text
Tüm projeyi rewrite etme.
Gereksiz dependency ekleme.
Mevcut servis sınırlarını bozma.
Task kapsamı dışındaki frontend/backend dosyalarını değiştirme.
Commit atma.
Migration’ı açıklamadan schema değiştirme.
FastAPI’yi stateful hale getirme.
LLM çıktısını doğrudan Neo4j’ye yazma.
```

Her task sonunda Codex şunları raporlamalıdır:

```text
Değişen dosyalar
Ne eklendi / ne değişti
Çalıştırılacak komutlar
Manuel kontrol checklist’i
Riskli veya eksik kalan noktalar
```

---

## 13. Dependency kuralları

Yeni dependency eklenirse açıklanmalıdır.

Her yeni dependency için:

```text
Neden gerekli?
Hangi app/package içinde kullanılıyor?
Alternatifi var mıydı?
.env.example güncellemesi gerekiyor mu?
Dockerfile güncellemesi gerekiyor mu?
```

Gereksiz framework eklenmemelidir.

Bu MVP’de aşağıdakiler default olarak eklenmemelidir:

```text
Qdrant
OpenSearch
Kafka
Temporal
RabbitMQ
Keycloak
OPA
LangGraph
LlamaIndex
Ragas
Langfuse
Prometheus
Grafana
Sentry
MinIO
Kubernetes
```

Bu teknolojiler future architecture kapsamıdır.

---

## 14. Test ve kontrol kuralları

Task türüne göre uygun kontroller yazılmalıdır.

Örnekler:

```text
npm run build
npm run lint
npm test
npx prisma validate
npx prisma generate
npx prisma migrate dev
uvicorn app.main:app --reload
curl /health
curl endpoint smoke test
docker compose up
```

Test yoksa en azından manuel kontrol adımları verilmelidir.

---

## 15. Doküman referans kuralı

Her task başında ilgili dokümanlar okunmalıdır.

Örnek:

```text
Prisma/data model task:
- docs/data-model-spec.md
- docs/fact-lifecycle.md
- docs/system-architecture.md

Validation task:
- docs/validation-review-policy.md
- docs/ontology-governance.md
- docs/fact-lifecycle.md

Semantic Memory task:
- docs/memory-taxonomy.md
- docs/data-model-spec.md
- docs/system-architecture.md
```

Task için gerekli olmayan tüm dokümanları okumaya zorlanmamalıdır. İlgili doküman subset’i yeterlidir.

---

## 16. Son kural

Bu projede mimari kararlar dokümanlarda ve kullanıcıda kalır. Codex’in görevi mimariyi yeniden icat etmek değil, verilen taskı mevcut mimari sınırları içinde uygulamaktır.

```text
Codex mimariyi değiştirmez.
Codex taskı uygular.
Kullanıcı diff’i inceler.
Commit kullanıcı tarafından atılır.
```

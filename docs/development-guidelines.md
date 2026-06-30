# Development Guidelines

## 1. Amaç

Bu dosya `kanat-mind-map` projesinde geliştirme yaparken uyulacak pratik kuralları tanımlar. Task listesi değildir. Task listesi tek kaynak olarak `codex-task-plan.md` dosyasında tutulur.

## 2. Servis sınırları

```text
apps/web sadece apps/api ile konuşur.
apps/api sistem sınırı ve veri sahibidir.
apps/ai-api stateless kalır ve DB'ye yazmaz.
Neo4j sadece curated graph projection tutar.
PostgreSQL workflow, review, evidence ve memory metadata kaynağıdır.
```

Yasaklar:

```text
Next.js → FastAPI direct call yok.
Next.js → Neo4j direct call yok.
FastAPI → PostgreSQL write yok.
FastAPI → Neo4j write yok.
LLM output → Neo4j direct publish yok.
```

## 3. Dependency ekleme kuralı

Yeni dependency eklenirken şunlar yazılmalıdır:

```text
Neden gerekli?
Hangi servise eklendi?
Alternatifi var mıydı?
.env.example değişti mi?
Dockerfile etkileniyor mu?
```

MVP dışı teknolojiler bilinçli olarak eklenmemelidir:

```text
Qdrant
OpenSearch
Kafka
Temporal
Keycloak
OPA
MinIO
Kubernetes
LangGraph
Ragas
```

Bu teknolojiler ileride mimariye eklenebilir ama MVP task'lerinde otomatik eklenmez.

## 4. Naming convention

```text
Markdown dosyaları: kebab-case English
API contract fields: camelCase
Prisma fields: camelCase
FastAPI internal fields: snake_case olabilir
FastAPI response fields: camelCase alias
Environment variables: UPPER_SNAKE_CASE
```

Örnek:

```text
evidenceAtomIds   API / NestJS / Prisma
evidence_atom_ids Python internal olabilir
```

## 5. Migration kuralı

Prisma migration yapılırken:

```text
Migration adı açıklayıcı olmalı.
Mevcut data kaybı yaratmamalı.
Breaking change varsa dokümanda belirtilmeli.
Migration sonrası prisma generate çalışmalı.
```

## 6. Status alanları

Hedef mimaride üç status ekseni vardır:

```text
reviewStatus
publicationStatus
validityStatus
```

MVP'de tek status alanı varsa bile yeni kod bu ayrımı bozmayacak şekilde yazılmalıdır.

## 7. Evidence kuralı

```text
CandidateFact evidenceAtomIds olmadan geçerli değildir.
GraphPatch evidence refs taşır.
PublishedAssertion evidence refs taşır.
SemanticMemoryItem evidence refs taşır.
LLM summary primary evidence olamaz.
```

## 8. Validation kuralı

Her candidate için validation sonucu izlenebilir olmalıdır.

Minimum kontroller:

```text
schema
ontology
evidence support
temporal
conflict
source authority placeholder
ACL placeholder
```

## 9. Review kuralı

Kritik bilgi auto-publish edilmez.

Zorunlu review örnekleri:

```text
role change
sales target
risk claim
price/discount
legal/contract info
conflict resolution
ontology change
```

## 10. Docker ve env kuralı

Her servis için `.env.example` güncel tutulmalıdır.

Örnek env'ler:

```text
DATABASE_URL
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
AI_API_BASE_URL
UPLOAD_DIR
LLM_API_BASE
LLM_API_KEY
LLM_MODEL_NAME
```

## 11. Test/kontrol beklentisi

Her task sonunda geliştirici şunları yazmalıdır:

```text
Değişen dosyalar
Çalıştırılan komutlar
Manuel kontrol adımları
Bilinen eksikler
Yeni env/dependency var mı?
```

## 12. Codex çalışma standardı

Codex'e verilecek promptlar küçük ve net olmalıdır.

İyi prompt:

```text
Sadece ValidationResult modelini ve POST /facts/:id/validate endpoint'ini ekle.
Mevcut upload/extract akışını değiştirme.
Commit atma.
Task sonunda çalıştırılacak komutları yaz.
```

Kötü prompt:

```text
Tüm projeyi yeni mimariye geçir.
```

## 13. Ana prensip

```text
Önce sınırlar.
Sonra contract.
Sonra model.
Sonra servis.
Sonra UI.
Sonra polish.
```

# Project Overview

## 1. Proje adı

```text
kanat-mind-map
```

Proje adı teknik mimarinin merkezinde değildir. İsim değişse bile ana amaç aynıdır: şirketin dağınık bilgisini kanıta bağlı, kontrol edilebilir ve sorgulanabilir bir kurumsal hafızaya dönüştürmek.

## 2. Kısa tanım

`kanat-mind-map`, şirket dokümanlarından ve operasyonel kaynaklardan evidence atomları üreten, LLM/agent ile candidate knowledge çıkaran, validation ve human review sonrası curated knowledge graph'a publish eden, ardından curated graph'tan öz semantic memory kartları oluşturan bir monorepo MVP'sidir.

Bu proje artık sadece 3-4 PDF alan basit bir demo değildir. Ama hâlâ kontrollü bir MVP'dir. Büyük hedef platform mimarisidir; ilk uygulama bu hedefin güvenli ve küçük çekirdeğini kurar.

## 3. Mevcut kabul edilen temel

Bu doküman seti aşağıdaki temellerin projede bulunduğunu varsayar:

```text
apps/web      Next.js frontend temeli
apps/api      NestJS backend temeli
apps/ai-api   FastAPI AI/document service temeli
Docker        her servis container içinde çalışabilir
PostgreSQL    operasyonel metadata ve workflow store
Neo4j          curated graph store
packages/ontology içinde örnek ontology
```

## 4. Ana hedef

Sistem şu sorulara güvenilir cevap verebilmelidir:

```text
Bu bilgi nereden geldi?
Bu bilgi şu an geçerli mi?
Bu bilgi insan tarafından onaylandı mı?
Bu bilgi hangi ontology kuralına göre üretildi?
Bu bilgi eski bir bilgi tarafından ezildi mi?
Bu konuda çelişki var mı?
Bu cevabın evidence'ı nedir?
```

## 5. Ana prensipler

```text
Archive her şeyi saklar.
Evidence kanıtlar.
Agent aday çıkarır.
Ontology sınır koyar.
Validation kontrol eder.
İnsan kritik kararları onaylar.
Graph patch değişikliği paketler.
Curated KG onaylı structured gerçekliği tutar.
Semantic Memory özü hatırlar.
Working Memory LLM'e küçük context verir.
```

## 6. MVP ve gelecek ayrımı

MVP'de amaç tüm enterprise sistemi kurmak değildir. Ama kavramsal sınırlar baştan doğru çizilir.

### MVP'de gerçeklenecekler

```text
PDF/TXT/MD upload
local file storage
EvidenceAtom üretimi
CandidateFact çıkarımı
basic validation
human review
GraphPatch proposal
approved patch publish
Neo4j curated graph
SemanticMemoryItem üretimi
basic ask
simple conflict handling
```

### Sonraki aşamalara bırakılacaklar

```text
Qdrant/pgvector/OpenSearch
Kafka/Temporal/RabbitMQ
Keycloak/OPA
MinIO/S3
LLM observability
Ragas/evaluation dashboard
advanced entity resolution service
ontology proposal UI
automated targeted re-extraction
production-grade ACL engine
```

## 7. Teknoloji stack

```text
Frontend:
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Flow

Backend:
- NestJS
- Prisma
- PostgreSQL
- Neo4j Driver

AI Service:
- FastAPI
- Pydantic
- PDF/TXT/MD parser
- OpenAI-compatible LLM client

Infra:
- Docker Compose
- PostgreSQL
- Neo4j
- Local file storage
```

## 8. Değişmez servis sınırları

```text
Next.js → NestJS
NestJS → FastAPI
NestJS → PostgreSQL
NestJS → Neo4j

FastAPI veritabanına yazmaz.
Next.js FastAPI, PostgreSQL veya Neo4j'ye doğrudan erişmez.
LLM output doğrudan Neo4j'ye yazılmaz.
Candidate bilgi resmi gerçek değildir.
```

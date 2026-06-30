# Singularity Mini KG Mimarisi

## Genel görünüm

Sistem üç uygulama, iki veri deposu ve ortak contract/ontology paketlerinden oluşur:

```text
Kullanıcı
   │
   ▼
apps/web (Next.js)
   │ HTTP
   ▼
apps/api (NestJS) ───────────────► PostgreSQL
   │                                  documents
   │ HTTP                             evidence_atoms
   ▼                                  candidate_facts
apps/ai-api (FastAPI)
   │
   └── structured JSON döner

apps/api (NestJS) ───────────────► Neo4j
                                    yalnızca published facts
```

## Bileşenler ve sorumluluklar

### `apps/web`

Next.js, React ve TypeScript tabanlı kullanıcı arayüzüdür. Document upload/list/detail, candidate fact review, graph viewer ve basic ask ekranlarını sunar. Yalnızca `apps/api` ile HTTP üzerinden konuşur; FastAPI, PostgreSQL veya Neo4j'ye doğrudan erişmez.

### `apps/api`

NestJS tabanlı sistem sınırı ve veri sahibidir. Dosya upload, validation, PostgreSQL persistence, human-review durum geçişleri, FastAPI orchestration, Neo4j publish, graph ve ask endpoint'lerinden sorumludur. Prisma ile PostgreSQL'e, Neo4j Driver ile Neo4j'ye erişir.

### `apps/ai-api`

FastAPI tabanlı stateless document-processing servisidir. PDF/TXT/MD metin çıkarma, evidence atom üretme, LLM çağrısı ve ontology validation işlemlerini yapar. Sonucu Pydantic ile doğrulanmış structured JSON olarak döner. PostgreSQL veya Neo4j'ye doğrudan yazmaz.

### `packages/contracts`

Servis sınırlarında kullanılan evidence atom, extracted fact ve graph JSON şemalarını tutar.

### `packages/ontology`

Demo boyunca kullanılmasına izin verilen entity ve relation tiplerinin merkezi kaynağıdır. LLM prompt'u, çıktı validasyonu ve review UI aynı ontology sözleşmesine dayanır.

## Veri sahipliği

PostgreSQL operasyonel kayıtların ana kaynağıdır:

- `documents`: dosya metadata ve işleme durumu
- `evidence_atoms`: dokümandan türetilen kaynak parçaları
- `candidate_facts`: LLM çıktısı, evidence bağlantıları, skorlar, geçerlilik ve review/publish durumu

Neo4j yalnızca insan tarafından onaylanıp yayımlanan bilgi grafını tutar. Candidate veya rejected fact'ler Neo4j'ye yazılmaz.

Yerel dosya sistemi demo için upload edilen dosyaların binary/text içeriğini tutar. PostgreSQL'deki `storagePath` bu dosyaya işaret eder.

## Temel veri akışı

### Ingestion ve extraction

1. Web, dosyayı ve `sourceType` bilgisini NestJS'e multipart form olarak gönderir.
2. NestJS desteklenen uzantıyı doğrular, dosyayı `UPLOAD_DIR` altında saklar ve document kaydı oluşturur.
3. Extract isteğinde NestJS, document'ın dosya yolunu FastAPI `/process-document` endpoint'ine gönderir.
4. FastAPI dosyayı parse eder, evidence atomlara böler ve LLM ile candidate fact çıkarır.
5. FastAPI sonucu JSON olarak NestJS'e döner; kalıcı yazımı NestJS yapar.

### Review ve publish

1. Candidate fact başlangıçta `candidate` durumundadır.
2. Kullanıcı subject, predicate, object, score ve validity alanlarını inceleyebilir/düzenleyebilir.
3. Kullanıcı fact'i `approved` veya `rejected` durumuna geçirir.
4. Publish endpoint'i yalnızca `approved` fact kabul eder.
5. NestJS subject/object node'larını ve relation'ı Neo4j'de idempotent biçimde `MERGE` eder.
6. Başarılı publish sonrasında PostgreSQL kaydı `published` olur ve `publishedAt` set edilir.

### Graph ve ask

NestJS, Neo4j'deki published graph'ı frontend'e node/edge JSON'u olarak sunar. Basic ask, serbest Cypher veya genel amaçlı LLM sorgusu yerine desteklenen intent'leri güvenli Cypher template'lerine eşler. Cevaplar evidence, approval score ve validity bilgisini taşır.

## Değişmez mimari sınırlar

```text
LLM output → candidate_facts → human approval → Neo4j publish
```

- `apps/web` yalnızca `apps/api` ile konuşur.
- `apps/api`, `apps/ai-api` ile HTTP üzerinden konuşur.
- `apps/ai-api` veritabanlarına yazmaz ve diğer uygulamaların iç dosyalarını import etmez.
- LLM çıktısı doğrudan Neo4j'ye yazılmaz.
- Sadece `approved` fact publish edilebilir.
- PostgreSQL review workflow'un, Neo4j published graph'ın kaynağıdır.

## Teknoloji seçimi

| Katman | Teknolojiler |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query/Table, React Hook Form, Zod, React Flow |
| Backend | NestJS, Prisma, PostgreSQL, Neo4j Driver |
| AI servisi | FastAPI, Pydantic, PyMuPDF veya pypdf, OpenAI-compatible LLM client |
| Altyapı | Docker Compose, PostgreSQL, Neo4j, local file storage |

## Hedef repo yapısı

```text
apps/
  web/
  api/
  ai-api/
packages/
  contracts/
  ontology/
mock-data/
  pdf/
  transcripts/
  software-notes/
docs/
```

Bu demo için Qdrant, pgvector, OpenSearch, Kafka, Temporal, RabbitMQ, BullMQ, Keycloak, OPA, LangGraph, LlamaIndex, Ragas, Langfuse, Prometheus, Grafana, Sentry, MinIO ve Kubernetes mimarinin parçası değildir.

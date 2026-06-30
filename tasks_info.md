# Singularity Mini KG Demo - Codex Task Plan

Bu doküman, **Singularity Mini KG Demo** projesini Codex destekli geliştirmek için hazırlanmış sıralı task planıdır.

Amaç, Codex'e tek seferde "tüm projeyi yap" demek yerine projeyi küçük, denetlenebilir, test edilebilir parçalara bölmektir.

Bu proje şu çekirdek akışı kanıtlar:

```text
PDF/TXT/MD Upload
→ Text Extraction
→ Evidence Atom Generation
→ LLM Candidate Fact Extraction
→ Approval Score + Validity Dates
→ Human Review
→ Neo4j Publish
→ Graph Viewer
→ Basic Ask
```

---

# FAZ 0 - Hazırlık

---

## Task 0.1 - Proje kapsam dokümanlarını yerleştir

### Amaç

Repo içine demo mimarisini anlatan dokümanları koymak.

### Yapılacaklar

```text
docs/demo-plan.md oluştur.
docs/architecture.md oluştur.
docs/evidence-atom-rules.md oluştur.
docs/codex-task-plan.md oluştur.
```

### Kabul kriteri

```text
docs klasörü var.
Demo kapsamı açıkça yazılmış.
Kapsam dışı teknolojiler açıkça yazılmış.
Codex task planı repo içinde bulunuyor.
```

### Codex prompt

```text
Bu repo Singularity Mini KG Demo projesidir.

Önce docs klasörü oluştur ve aşağıdaki dokümanları ekle:
- docs/demo-plan.md
- docs/architecture.md
- docs/evidence-atom-rules.md
- docs/codex-task-plan.md

Bu dokümanlarda şu temel fikri açıkla:
PDF/TXT/MD dosyaları upload edilir, text extraction yapılır, evidence atom üretilir, LLM candidate fact çıkarır, fact approval_score ve valid_from/valid_until taşır, kullanıcı onaylar, approved facts Neo4j knowledge graph'a publish edilir, frontend graph viewer ve basic ask ekranı sunar.

Bu task'ta kod yazma. Sadece dokümantasyon oluştur.
Commit atma.
```

---

## Task 0.2 - Demo ontology dosyasını oluştur

### Amaç

İzinli entity ve relation tiplerini merkezi bir YAML dosyasında tutmak.

### Dosya

```text
packages/ontology/demo-ontology.yaml
```

### Entity tipleri

```text
Customer
Person
Team
Region
Product
Project
Service
Risk
SalesTarget
Decision
Document
```

### Relation tipleri

```text
managedBy
locatedIn
interestedIn
hasTarget
hasRisk
memberOf
ownsService
partOf
dependsOn
decidedIn
affects
mentions
```

### Kabul kriteri

```text
demo-ontology.yaml var.
Her entity için description var.
Her relation için from/to tipi var.
Relation'ların subject/object kuralları açık.
```

### Codex prompt

```text
packages/ontology/demo-ontology.yaml dosyasını oluştur.

Entity tipleri:
Customer, Person, Team, Region, Product, Project, Service, Risk, SalesTarget, Decision, Document

Relation tipleri:
managedBy, locatedIn, interestedIn, hasTarget, hasRisk, memberOf, ownsService, partOf, dependsOn, decidedIn, affects, mentions

Her relation için:
- description
- from
- to
- evidence_required: true
alanlarını ekle.

mentions relation için to: "*" olabilir.

Commit atma.
```

---

# FAZ 1 - Monorepo ve infra

---

## Task 1.1 - Monorepo iskeletini oluştur

### Amaç

Proje klasör yapısını kurmak.

### Yapılacaklar

```text
apps/web
apps/api
apps/ai-api
packages/contracts
packages/ontology
mock-data
docs
```

### Kabul kriteri

```text
Klasör yapısı oluştu.
Root README.md oluştu.
Root .gitignore oluştu.
Root .env.example oluştu.
```

### Codex prompt

```text
Monorepo iskeletini oluştur.

Klasörler:
- apps/web
- apps/api
- apps/ai-api
- packages/contracts
- packages/ontology
- mock-data/pdf
- mock-data/transcripts
- mock-data/software-notes
- docs

Root README.md, .gitignore ve .env.example dosyalarını oluştur.

README içinde:
- Proje amacı
- Servisler
- Local geliştirme mantığı
- Henüz kurulum komutlarının sonraki task'lerde ekleneceğini belirt.

Bu task'ta framework kurulumu yapma.
Commit atma.
```

---

## Task 1.2 - Docker Compose ile PostgreSQL ve Neo4j ekle

### Amaç

Demo için temel database ve graph altyapısını ayağa kaldırmak.

### Servisler

```text
postgres
neo4j
```

### Portlar

```text
PostgreSQL: 5432
Neo4j Browser: 7474
Neo4j Bolt: 7687
```

### Env

```text
POSTGRES_USER=singularity
POSTGRES_PASSWORD=singularity
POSTGRES_DB=singularity_demo

NEO4J_AUTH=neo4j/password123
```

### Kabul kriteri

```text
docker compose up -d postgres neo4j çalışır.
PostgreSQL container çalışır.
Neo4j browser http://localhost:7474 açılır.
```

### Codex prompt

```text
Root docker-compose.yml dosyasını oluştur.

Servisler:
- postgres:16-alpine
- neo4j:latest

PostgreSQL:
POSTGRES_USER=singularity
POSTGRES_PASSWORD=singularity
POSTGRES_DB=singularity_demo
port 5432:5432

Neo4j:
NEO4J_AUTH=neo4j/password123
ports:
7474:7474
7687:7687

Volume'lar:
postgres_data
neo4j_data

Root README.md içine docker compose up -d postgres neo4j komutunu ekle.

Commit atma.
```

---

## Task 1.3 - Next.js app oluştur

### Amaç

Frontend uygulamasını kurmak.

### Stack

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
```

### Kabul kriteri

```text
apps/web içinde Next.js app çalışır.
npm run dev ile açılır.
Ana sayfada Singularity Mini KG Demo başlığı görünür.
```

### Codex prompt

```text
apps/web içinde Next.js + TypeScript + Tailwind CSS uygulaması oluştur.

shadcn/ui kurulumu için gerekli temel ayarları ekle.
Ana sayfada şu başlık görünsün:
Singularity Mini KG Demo

Henüz API bağlantısı yapma.
Root README.md içine apps/web çalıştırma komutlarını ekle.

Commit atma.
```

---

## Task 1.4 - NestJS app oluştur

### Amaç

Ana backend uygulamasını kurmak.

### Kabul kriteri

```text
apps/api içinde NestJS uygulaması var.
npm run start:dev çalışıyor.
GET /health endpoint'i { status: "ok" } dönüyor.
```

### Codex prompt

```text
apps/api içinde NestJS uygulaması oluştur.

GET /health endpoint'i ekle.
Response:
{ "status": "ok" }

.env.example dosyasına şunları ekle:
DATABASE_URL
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
AI_API_BASE_URL
UPLOAD_DIR

Root README.md içine apps/api çalıştırma komutlarını ekle.

Commit atma.
```

---

## Task 1.5 - FastAPI app oluştur

### Amaç

AI/document processing servisinin temelini kurmak.

### Kabul kriteri

```text
apps/ai-api içinde FastAPI uygulaması var.
uvicorn app.main:app --reload --port 8000 çalışıyor.
GET /health endpoint'i { status: "ok" } dönüyor.
```

### Codex prompt

```text
apps/ai-api içinde FastAPI uygulaması oluştur.

Dosya yapısı:
app/
  main.py
  core/config.py
  schemas/
  services/
  api/

GET /health endpoint'i ekle.
Response:
{ "status": "ok" }

requirements.txt oluştur.
Gerekli minimum dependency'leri ekle:
fastapi
uvicorn
pydantic
python-dotenv

.env.example oluştur:
LLM_API_BASE
LLM_API_KEY
LLM_MODEL_NAME

Root README.md içine apps/ai-api çalıştırma komutlarını ekle.

Commit atma.
```

---

# FAZ 2 - NestJS API ve database

---

## Task 2.1 - Prisma ve PostgreSQL bağlantısını kur

### Amaç

NestJS API'nin PostgreSQL ile çalışmasını sağlamak.

### Kabul kriteri

```text
Prisma kurulu.
DATABASE_URL ile PostgreSQL'e bağlanıyor.
npx prisma migrate dev çalışıyor.
PrismaService var.
```

### Codex prompt

```text
apps/api içinde Prisma kurulumunu yap.

DATABASE_URL:
postgresql://singularity:singularity@localhost:5432/singularity_demo

PrismaService oluştur.
AppModule içinde PrismaModule kullan.

Şimdilik boş schema veya sadece temel Document modeli eklenebilir.
Migration komutlarını README'ye ekle.

Commit atma.
```

---

## Task 2.2 - Document model ve documents module oluştur

### Amaç

Yüklenen dosyaların metadata kayıtlarını tutmak.

### Prisma model

```prisma
model Document {
  id          String   @id @default(cuid())
  fileName    String
  fileType    String
  sourceType  String
  storagePath String
  status      String   @default("uploaded")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

### Endpointler

```text
GET /documents
GET /documents/:id
```

### Kabul kriteri

```text
Document modeli var.
Migration çalışıyor.
GET /documents boş liste dönüyor.
GET /documents/:id bulunamazsa 404 dönüyor.
```

### Codex prompt

```text
NestJS apps/api içinde documents modülü oluştur.

Prisma schema'ya Document modelini ekle:
id, fileName, fileType, sourceType, storagePath, status, createdAt, updatedAt

Endpointler:
GET /documents
GET /documents/:id

DTO ve service yapısını düzgün kur.
Bulunamayan document için 404 dön.

Migration oluştur ama commit atma.
Çalıştırılacak komutları cevapta yaz.
```

---

## Task 2.3 - File upload endpoint'i ekle

### Amaç

PDF/TXT/MD dosyalarını upload etmek.

### Endpoint

```text
POST /documents/upload
```

### Desteklenen dosya tipleri

```text
application/pdf
text/plain
text/markdown
.md
.txt
.pdf
```

### Kabul kriteri

```text
Dosya local uploads klasörüne kaydedilir.
Document kaydı PostgreSQL'e yazılır.
Response document objesini döner.
Unsupported file type 400 döner.
```

### Codex prompt

```text
NestJS documents modülüne POST /documents/upload endpoint'i ekle.

Gereksinimler:
- multipart/form-data ile file al.
- sourceType alanı da alınsın. Değerler: pdf, transcript, software_note
- Desteklenen uzantılar: .pdf, .txt, .md
- Dosyayı UPLOAD_DIR altında sakla.
- Document kaydını PostgreSQL'e yaz.
- status = uploaded olsun.
- Unsupported file type için 400 dön.

.env.example içine UPLOAD_DIR ekle.
README'ye upload örnek curl komutu ekle.

Commit atma.
```

---

## Task 2.4 - EvidenceAtom modelini ekle

### Amaç

Document'tan çıkarılan evidence atomları saklamak.

### Prisma model

```prisma
model EvidenceAtom {
  id          String   @id @default(cuid())
  documentId  String
  atomIndex   Int
  atomType    String
  sourceType  String
  pageNumber  Int?
  sectionPath Json?
  text        String
  qualityScore Int?
  charStart   Int?
  charEnd     Int?
  hash        String?
  metadata    Json?
  createdAt   DateTime @default(now())

  document Document @relation(fields: [documentId], references: [id])
}
```

### Endpointler

```text
GET /documents/:id/evidence-atoms
```

### Kabul kriteri

```text
EvidenceAtom modeli var.
Document relation var.
GET /documents/:id/evidence-atoms çalışır.
```

### Codex prompt

```text
Prisma schema'ya EvidenceAtom modelini ekle.

Alanlar:
id, documentId, atomIndex, atomType, sourceType, pageNumber, sectionPath, text, qualityScore, charStart, charEnd, hash, metadata, createdAt

Document ile relation kur.

NestJS documents modülüne GET /documents/:id/evidence-atoms endpoint'i ekle.

Migration oluştur.
Commit atma.
```

---

## Task 2.5 - CandidateFact modelini ekle

### Amaç

LLM tarafından çıkarılan aday fact'leri saklamak.

### Prisma model

```prisma
model CandidateFact {
  id              String   @id @default(cuid())
  subjectName     String
  subjectType     String
  predicate       String
  objectName      String
  objectType      String
  objectProperties Json?
  evidenceAtomIds Json
  sourceDocumentId String
  evidenceText    String?
  llmConfidence   Float
  approvalScore   Int
  status          String   @default("candidate")
  validFrom       DateTime?
  validUntil      DateTime?
  publishedAt     DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}
```

### Endpointler

```text
GET /facts/candidates
GET /facts/:id
PATCH /facts/:id
POST /facts/:id/approve
POST /facts/:id/reject
```

### Kabul kriteri

```text
CandidateFact modeli var.
Candidate facts listelenir.
Fact editlenebilir.
Approve status'u approved yapar.
Reject status'u rejected yapar.
```

### Codex prompt

```text
NestJS içinde facts modülü oluştur.

Prisma schema'ya CandidateFact modelini ekle:
id, subjectName, subjectType, predicate, objectName, objectType, objectProperties, evidenceAtomIds, sourceDocumentId, evidenceText, llmConfidence, approvalScore, status, validFrom, validUntil, publishedAt, createdAt, updatedAt

Endpointler:
GET /facts/candidates
GET /facts/:id
PATCH /facts/:id
POST /facts/:id/approve
POST /facts/:id/reject

PATCH ile şu alanlar güncellenebilsin:
subjectName, subjectType, predicate, objectName, objectType, objectProperties, approvalScore, validFrom, validUntil, status

Approve status'u approved yapmalı.
Reject status'u rejected yapmalı.

Migration oluştur.
Commit atma.
```

---

# FAZ 3 - FastAPI document processing

---

## Task 3.1 - FastAPI parser schema'larını oluştur

### Amaç

FastAPI'nin structured JSON dönmesi için Pydantic schema'larını oluşturmak.

### Schema'lar

```text
DocumentProcessRequest
EvidenceAtom
ExtractedFact
ProcessDocumentResponse
```

### Kabul kriteri

```text
Pydantic modeller var.
OpenAPI docs'ta görünür.
```

### Codex prompt

```text
apps/ai-api içinde Pydantic schema'larını oluştur.

Dosya:
app/schemas/document_processing.py

Modeller:
- DocumentProcessRequest
  file_path: str
  file_name: str
  source_type: str

- EvidenceAtom
  atom_id: str
  atom_index: int
  atom_type: str
  source_type: str
  page_number: int | None
  section_path: list[str]
  text: str
  quality_score: int | None
  char_start: int | None
  char_end: int | None
  metadata: dict

- ExtractedFact
  subject: dict
  predicate: str
  object: dict
  evidence_atom_ids: list[str]
  evidence_text: str | None
  llm_confidence: float
  approval_score: int
  valid_from: str | None
  valid_until: str | None

- ProcessDocumentResponse
  evidence_atoms: list[EvidenceAtom]
  candidate_facts: list[ExtractedFact]

Commit atma.
```

---

## Task 3.2 - PDF/TXT/MD text extraction service yaz

### Amaç

Dosya türüne göre text çıkarma.

### Destek

```text
PDF: PyMuPDF veya pypdf
TXT: direct read
MD: direct read
```

### Kabul kriteri

```text
PDF text çıkarılır.
TXT okunur.
MD okunur.
Unsupported extension hata verir.
```

### Codex prompt

```text
apps/ai-api içinde document parser service oluştur.

Dosya:
app/services/document_parser_service.py

Desteklenen dosyalar:
- .pdf için PyMuPDF veya pypdf kullan.
- .txt için utf-8 direct read.
- .md için utf-8 direct read.

Output olarak şu yapıyı dön:
{
  "pages": [
    {
      "page_number": 1,
      "text": "..."
    }
  ]
}

TXT/MD için page_number null veya 1 olabilir.

requirements.txt içine gerekli PDF parser dependency'sini ekle.

Commit atma.
```

---

## Task 3.3 - Evidence atom generator service yaz

### Amaç

Text'i anlamlı evidence atomlarına bölmek.

### Kurallar

PDF:

```text
Sayfa bazlı text al.
Boş satır/paragraf bazlı böl.
1500 karakter üstünü cümle bazlı parçala.
80 karakter altı bağlamsız satırları komşusuyla birleştir.
```

Transcript:

```text
Speaker turn'leri ayır.
Karar/Aksiyon/Risk/Not bloklarını ayrı atom yap.
```

Markdown:

```text
Başlıkları section_path yap.
Bullet ve teknik cümleleri atom yap.
```

### Kabul kriteri

```text
Evidence atom listesi üretilir.
Her atom atom_id, atom_index, atom_type, text taşır.
quality_score hesaplanır.
```

### Codex prompt

```text
apps/ai-api içinde evidence atom generator service oluştur.

Dosya:
app/services/evidence_atom_service.py

Fonksiyon:
create_evidence_atoms(parsed_document, source_type, file_name) -> list[EvidenceAtom]

Kurallar:
- PDF için paragraph atomları üret.
- Transcript için speaker turn ve decision_block atomları üret.
- Markdown için heading section_path ve paragraph/bullet atomları üret.
- 1500 karakterden uzun atomları cümle bazlı böl.
- Çok kısa ve bağlamsız atomları komşusuyla birleştir.
- quality_score basit heuristic ile hesaplansın.
- atom_id stabil ve okunabilir olsun:
  örnek: docslug:a001

Commit atma.
```

---

## Task 3.4 - /process-document endpoint'ini ekle

### Amaç

FastAPI'nin file path alıp atoms döndürmesi.

### Endpoint

```text
POST /process-document
```

### Kabul kriteri

```text
file_path gönderildiğinde evidence_atoms döner.
candidate_facts şimdilik boş liste olabilir.
```

### Codex prompt

```text
FastAPI içinde POST /process-document endpoint'i ekle.

Input:
DocumentProcessRequest

Akış:
- file_path ve source_type al.
- document_parser_service ile text çıkar.
- evidence_atom_service ile evidence atoms üret.
- Response içinde evidence_atoms dön.
- candidate_facts şimdilik boş liste dön.

Hata durumları:
- file not found
- unsupported file type
- parser error

Commit atma.
```

---

# FAZ 4 - LLM candidate fact extraction

---

## Task 4.1 - LLM client abstraction oluştur

### Amaç

LLM provider değişse bile extraction servisinin değişmemesi.

### Kabul kriteri

```text
LLMClient sınıfı var.
chat_json metodu var.
Env'den LLM_API_BASE, LLM_API_KEY, LLM_MODEL_NAME okur.
```

### Codex prompt

```text
apps/ai-api içinde LLM client abstraction oluştur.

Dosya:
app/services/llm_client.py

Env:
LLM_API_BASE
LLM_API_KEY
LLM_MODEL_NAME

OpenAI-compatible chat completions endpoint varsay.
chat_json(system_prompt: str, user_prompt: str) -> dict metodu olsun.

Hata handling ekle.
Response JSON parse edilemezse anlaşılır hata dön.

Commit atma.
```

---

## Task 4.2 - Fact extraction prompt ve ontology validation ekle

### Amaç

LLM'in sadece izinli entity/relation tipleriyle fact çıkarması.

### Kabul kriteri

```text
Prompt template var.
Allowed entity/relation listesi kullanılır.
LLM çıktısı Pydantic ile validate edilir.
Ontology dışı fact filtrelenir veya rejected olarak işaretlenir.
```

### Codex prompt

```text
apps/ai-api içinde fact extraction service oluştur.

Dosya:
app/services/fact_extraction_service.py

Görev:
- Evidence atomları 5-10 atomluk batch'lere böl.
- Her batch'i LLM'e gönder.
- Prompt içinde allowed entity types ve relation types belirt.
- LLM'den JSON facts iste.
- Her fact için evidence_atom_ids zorunlu olsun.
- valid_from ve valid_until tarihleri çıkarılsın.
- llm_confidence 0-1 arası olsun.
- approval_score = round(llm_confidence * 100) olarak hesaplansın.

Allowed ontology:
Entity:
Customer, Person, Team, Region, Product, Project, Service, Risk, SalesTarget, Decision, Document

Relations:
managedBy, locatedIn, interestedIn, hasTarget, hasRisk, memberOf, ownsService, partOf, dependsOn, decidedIn, affects, mentions

Commit atma.
```

---

## Task 4.3 - /process-document endpoint'ine fact extraction ekle

### Amaç

FastAPI'nin atoms + candidate facts döndürmesi.

### Kabul kriteri

```text
POST /process-document evidence_atoms ve candidate_facts döner.
Her fact evidence_atom_ids taşır.
Her fact approval_score taşır.
Her fact valid_from/valid_until alanlarına sahiptir.
```

### Codex prompt

```text
POST /process-document endpoint'ini güncelle.

Akış:
- file parse edilir.
- evidence atoms üretilir.
- fact_extraction_service ile candidate facts çıkarılır.
- Response içinde evidence_atoms ve candidate_facts birlikte dönülür.

Eğer LLM env tanımlı değilse veya LLM çağrısı başarısız olursa:
- evidence_atoms dön.
- candidate_facts boş liste dön.
- response metadata içinde warning ekle.

Gerekirse ProcessDocumentResponse schema'sını metadata/warnings destekleyecek şekilde güncelle.

Commit atma.
```

---

## Task 4.4 - NestJS extract endpoint'i FastAPI ile entegre et

### Amaç

Document extract butonu ile FastAPI'den atoms/facts almak ve PostgreSQL'e kaydetmek.

### Endpoint

```text
POST /documents/:id/extract
```

### Kabul kriteri

```text
Document bulunur.
FastAPI /process-document çağrılır.
Evidence atoms PostgreSQL'e yazılır.
Candidate facts PostgreSQL'e yazılır.
Document status extracted olur.
```

### Codex prompt

```text
NestJS apps/api içinde POST /documents/:id/extract endpoint'ini ekle.

Akış:
- Document id ile document bulunur.
- storagePath FastAPI /process-document endpoint'ine gönderilir.
- Dönen evidence_atoms PostgreSQL EvidenceAtom tablosuna yazılır.
- Dönen candidate_facts PostgreSQL CandidateFact tablosuna yazılır.
- sourceDocumentId document.id olsun.
- Document status = extracted yapılır.
- Eğer FastAPI hata verirse document status = failed yapılabilir.

AI_API_BASE_URL env değerini kullan.
HTTP client service oluştur.

Commit atma.
```

---

# FAZ 5 - Frontend temel ekranlar

---

## Task 5.1 - Frontend API client ve layout oluştur

### Amaç

Next.js içinde API çağrıları ve ana layout'u hazırlamak.

### Kabul kriteri

```text
NEXT_PUBLIC_API_BASE_URL kullanılır.
api client helper var.
Ana navigasyon var.
Sayfalar arası geçiş var.
```

### Codex prompt

```text
apps/web içinde temel layout ve API client oluştur.

Sayfalar:
- /
- /documents
- /facts
- /graph
- /ask

Navigation:
Documents
Candidate Facts
Graph
Ask

NEXT_PUBLIC_API_BASE_URL env değerini kullanarak basit fetch wrapper oluştur.
TanStack Query kurulumunu yap.

shadcn/ui bileşenlerini kullanmaya hazır hale getir.

Commit atma.
```

---

## Task 5.2 - Document upload ekranı

### Amaç

Kullanıcı PDF/TXT/MD upload edebilsin.

### Kabul kriteri

```text
Upload form var.
sourceType seçilir.
Dosya seçilir.
Upload başarılı olunca documents list yenilenir.
```

### Codex prompt

```text
apps/web içinde /documents sayfasına document upload formu ekle.

Alanlar:
- file input
- sourceType select: pdf, transcript, software_note
- upload button

POST /documents/upload endpoint'ine multipart/form-data gönder.
Upload başarılı olunca documents list yenilensin.

shadcn/ui kullan.
Hata ve loading state göster.

Commit atma.
```

---

## Task 5.3 - Documents list ve extract butonu

### Amaç

Yüklenen dosyaları listelemek ve extraction başlatmak.

### Kabul kriteri

```text
Documents list görünür.
Status görünür.
Extract butonu çalışır.
Extract sonrası status güncellenir.
```

### Codex prompt

```text
/apps/web /documents sayfasında documents list tablosu oluştur.

Kolonlar:
- fileName
- sourceType
- status
- createdAt
- actions

Actions:
- Extract button
- View details link

Extract button POST /documents/:id/extract çağırmalı.
Loading state göster.
Başarılı olunca documents query invalidate edilsin.

Commit atma.
```

---

## Task 5.4 - Document detail ekranı

### Amaç

Bir document'ın evidence atoms ve facts bilgilerini görmek.

### Route

```text
/documents/[id]
```

### Kabul kriteri

```text
Document metadata görünür.
Evidence atoms listelenir.
Document facts listelenir.
```

### Codex prompt

```text
apps/web içinde /documents/[id] detail sayfası oluştur.

Gösterilecekler:
- document metadata
- evidence atoms
- candidate facts

Backend endpointleri:
GET /documents/:id
GET /documents/:id/evidence-atoms
GET /documents/:id/facts

Eğer /documents/:id/facts endpoint'i yoksa NestJS tarafına da ekle.

Commit atma.
```

---

# FAZ 6 - Candidate facts ve human review

---

## Task 6.1 - Candidate facts list ekranı

### Amaç

Tüm candidate fact'leri tablo halinde görmek.

### Route

```text
/facts
```

### Kabul kriteri

```text
Subject, Predicate, Object, Score, Validity, Status görünür.
Filtre yoksa bile liste çalışır.
```

### Codex prompt

```text
apps/web içinde /facts sayfasını oluştur.

GET /facts/candidates endpoint'inden facts çek.

Tablo kolonları:
- subjectName
- predicate
- objectName
- approvalScore
- validFrom
- validUntil
- status
- actions

TanStack Table veya basit tablo kullan.
shadcn/ui kullan.
Loading/error state ekle.

Commit atma.
```

---

## Task 6.2 - Fact detail/edit drawer veya dialog

### Amaç

Fact'i düzenlemek ve evidence görmek.

### Kabul kriteri

```text
Satıra tıklanınca detay açılır.
Evidence text görünür.
Score ve validity editlenir.
Save PATCH /facts/:id çağırır.
```

### Codex prompt

```text
/facts sayfasına fact detail/edit dialog ekle.

Detayda göster:
- subjectName
- subjectType
- predicate
- objectName
- objectType
- evidenceText
- llmConfidence
- approvalScore
- validFrom
- validUntil
- status

Editlenebilir alanlar:
- subjectName
- subjectType
- predicate
- objectName
- objectType
- approvalScore
- validFrom
- validUntil
- status

Save butonu PATCH /facts/:id çağırmalı.

Commit atma.
```

---

## Task 6.3 - Approve/reject aksiyonları

### Amaç

Human review akışını mini düzeyde tamamlamak.

### Kabul kriteri

```text
Approve butonu status approved yapar.
Reject butonu status rejected yapar.
UI güncellenir.
```

### Codex prompt

```text
/facts sayfasına approve/reject butonları ekle.

Approve:
POST /facts/:id/approve

Reject:
POST /facts/:id/reject

İşlemden sonra facts list invalidate edilsin.
Status badge ile gösterilsin:
candidate, approved, rejected, published

Commit atma.
```

---

# FAZ 7 - Neo4j publish ve graph viewer

---

## Task 7.1 - NestJS Neo4j service oluştur

### Amaç

NestJS'in Neo4j ile konuşabilmesi.

### Kabul kriteri

```text
Neo4j bağlantısı env'den okunur.
Service lifecycle düzgün kapanır.
Health kontrolü yapılabilir.
```

### Codex prompt

```text
NestJS apps/api içinde Neo4jModule ve Neo4jService oluştur.

Env:
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD

Neo4j driver kullan.
Service içinde run(query, params) helper metodu olsun.
Uygulama kapanırken driver close edilsin.

GET /health endpoint'i Neo4j bağlantı durumunu da opsiyonel gösterebilir.

Commit atma.
```

---

## Task 7.2 - Fact publish endpoint'i ekle

### Amaç

Approved fact'i Neo4j'ye yazmak.

### Endpoint

```text
POST /facts/:id/publish
```

### Kabul kriteri

```text
Sadece approved fact publish edilir.
Subject node MERGE edilir.
Object node MERGE edilir.
Relation MERGE edilir.
Relation metadata yazılır.
Fact status published olur.
publishedAt set edilir.
```

### Codex prompt

```text
NestJS facts modülüne POST /facts/:id/publish endpoint'i ekle.

Kurallar:
- Sadece status = approved olan fact publish edilebilir.
- rejected/candidate fact publish edilemez.
- Subject node type'a göre label almalı.
- Object node type'a göre label almalı.
- Relation predicate uppercase snake case'e çevrilmeli:
  managedBy -> MANAGED_BY
  locatedIn -> LOCATED_IN
  interestedIn -> INTERESTED_IN
  hasTarget -> HAS_TARGET
  hasRisk -> HAS_RISK
  memberOf -> MEMBER_OF
  ownsService -> OWNS_SERVICE
  partOf -> PART_OF
  dependsOn -> DEPENDS_ON
  decidedIn -> DECIDED_IN
  affects -> AFFECTS
  mentions -> MENTIONS

Relation property'leri:
- factId
- approvalScore
- llmConfidence
- validFrom
- validUntil
- sourceDocumentId
- evidenceAtomIds
- evidenceText
- status = published

Publish sonrası CandidateFact status = published, publishedAt = now yapılmalı.

Commit atma.
```

---

## Task 7.3 - Graph API endpoint'i ekle

### Amaç

Neo4j graph'ını frontend graph viewer formatında döndürmek.

### Endpoint

```text
GET /graph
```

### Response

```json
{
  "nodes": [
    {
      "id": "Customer:ABC Boya",
      "label": "ABC Boya",
      "type": "Customer",
      "properties": {}
    }
  ],
  "edges": [
    {
      "id": "fact_001",
      "source": "Customer:ABC Boya",
      "target": "Person:Ahmet Yılmaz",
      "label": "MANAGED_BY",
      "properties": {}
    }
  ]
}
```

### Kabul kriteri

```text
GET /graph published graph döner.
Frontend React Flow formatına yakın data döner.
```

### Codex prompt

```text
NestJS içinde graph modülü oluştur.

GET /graph endpoint'i Neo4j'den published graph verisini çeksin.

Response:
{
  nodes: [
    { id, label, type, properties }
  ],
  edges: [
    { id, source, target, label, properties }
  ]
}

Node id formatı:
Label:name

Edge id:
relation.factId varsa factId, yoksa generated id

Commit atma.
```

---

## Task 7.4 - Frontend graph viewer ekranı

### Amaç

Published graph'ı React Flow ile göstermek.

### Route

```text
/graph
```

### Kabul kriteri

```text
Node ve edge görünür.
Edge label görünür.
Edge'e tıklayınca detail panel açılır.
Evidence, score, validity görünür.
```

### Codex prompt

```text
apps/web içinde /graph sayfasını oluştur.

GET /graph endpoint'inden graph data çek.
React Flow ile node/edge göster.

Gereksinimler:
- Node label entity name olsun.
- Node altında type küçük yazabilir.
- Edge label relation label olsun.
- Edge'e tıklanınca sağ panel veya dialog açılsın.
- Detail panelde:
  approvalScore
  llmConfidence
  validFrom
  validUntil
  evidenceText
  sourceDocumentId
gösterilsin.

Commit atma.
```

---

# FAZ 8 - Basic ask

---

## Task 8.1 - Ask endpoint'i için query intent parser

### Amaç

Kullanıcı sorusunu basit template query tiplerine ayırmak.

### Desteklenecek sorular

```text
X kimden sorumlu?
X hangi bölgede?
X hedefi ne?
X riskleri neler?
X hangi projenin parçası?
X hangi servise bağımlı?
X'in sahibi kim?
```

### Kabul kriteri

```text
Soru intent'e ayrılır.
Entity name kabaca çıkarılır.
Unsupported question için açıklayıcı response döner.
```

### Codex prompt

```text
NestJS içinde ask modülü oluştur.

POST /ask endpoint'i ekle.

Input:
{ "question": "ABC Boya'dan kim sorumlu?" }

İlk aşamada LLM kullanma.
Basit string matching ile intent belirle.

Desteklenen intent'ler:
- customerManagedBy
- customerLocatedIn
- customerTarget
- customerRisks
- servicePartOfProject
- serviceDependsOn
- serviceOwner

Entity name extraction basit olabilir:
Soru içindeki bilinen kalıpları çıkararak kalan kısmı entityName kabul et.

Unsupported soru için:
{
  answer: "Bu demo şu an bu soru tipini desteklemiyor.",
  supportedExamples: [...]
}

Commit atma.
```

---

## Task 8.2 - Ask endpoint'i Cypher template query'leri

### Amaç

Intent'e göre Neo4j query çalıştırmak.

### Kabul kriteri

```text
Desteklenen 7 soru tipi çalışır.
Cevap evidence ve approval score içerir.
```

### Codex prompt

```text
POST /ask endpoint'ine Neo4j template query'leri ekle.

Intent'e göre query çalıştır:
- Customer -[:MANAGED_BY]-> Person
- Customer -[:LOCATED_IN]-> Region
- Customer -[:HAS_TARGET]-> SalesTarget
- Customer -[:HAS_RISK]-> Risk
- Service -[:PART_OF]-> Project
- Service -[:DEPENDS_ON]-> Service
- Team -[:OWNS_SERVICE]-> Service veya Service owner lookup için ters yönde query

Response:
{
  answer: string,
  matches: [
    {
      subject,
      predicate,
      object,
      evidenceText,
      approvalScore,
      validFrom,
      validUntil
    }
  ]
}

Commit atma.
```

---

## Task 8.3 - Frontend ask ekranı

### Amaç

Kullanıcı basic ask ekranından soru sorabilsin.

### Route

```text
/ask
```

### Kabul kriteri

```text
Input var.
Soru gönderilir.
Cevap görünür.
Evidence görünür.
Supported examples görünür.
```

### Codex prompt

```text
apps/web içinde /ask sayfasını oluştur.

UI:
- soru input'u
- ask button
- örnek sorular listesi
- cevap kartı
- evidence/matches listesi

POST /ask endpoint'ine soru gönder.
Loading/error state ekle.

Örnek sorular:
- ABC Boya'dan kim sorumlu?
- ABC Boya hangi bölgede?
- ABC Boya'nın hedefi ne?
- ABC Boya'nın riskleri neler?
- CRM Sync Service hangi projenin parçası?
- CRM Sync Service hangi servise bağımlı?
- CRM Sync Service'in sahibi kim?

Commit atma.
```

---

# FAZ 9 - Demo polish, seed ve test

---

## Task 9.1 - Mock data klasörünü yerleştir

### Amaç

Daha önce oluşturulan mock data dosyalarını repo içine koymak.

### Klasör

```text
mock-data/
  pdf/
  transcripts/
  software-notes/
  expected/
  manifest.json
  README.md
```

### Kabul kriteri

```text
Mock data repo içinde var.
README mock data kullanımını anlatır.
```

### Codex prompt

```text
mock-data klasörünü düzenle.

Beklenen yapı:
mock-data/pdf
mock-data/transcripts
mock-data/software-notes
mock-data/expected
mock-data/manifest.json
mock-data/README.md

Eğer dosyalar zaten varsa koru.
README içine bu dosyaların demo upload için kullanılacağını yaz.

Kod yazma.
Commit atma.
```

---

## Task 9.2 - Seed/import helper script

### Amaç

Mock dataları manuel tek tek UI'dan yüklemek yerine opsiyonel script ile upload etmek.

### Kabul kriteri

```text
Script mock-data dosyalarını API'ye upload edebilir.
Script opsiyoneldir.
README'de kullanımı yazılıdır.
```

### Codex prompt

```text
Opsiyonel bir mock data upload script'i ekle.

Konum:
scripts/upload-mock-data.ts veya scripts/upload-mock-data.js

Görev:
- mock-data/pdf altındaki PDF'leri sourceType=pdf ile upload et.
- mock-data/transcripts altındaki TXT'leri sourceType=transcript ile upload et.
- mock-data/software-notes altındaki MD'leri sourceType=software_note ile upload et.
- API base URL env veya argümandan alınsın.

Bu script opsiyonel olsun; UI upload akışını bozmasın.
README'ye kullanımını ekle.

Commit atma.
```

---

## Task 9.3 - Basic validation ve error handling polish

### Amaç

Demo esnasında sistemin kolay kırılmasını önlemek.

### Kabul kriteri

```text
Upload hataları düzgün görünür.
Extraction hataları düzgün görünür.
Publish hataları düzgün görünür.
Unsupported ask soruları düzgün cevaplanır.
```

### Codex prompt

```text
Projede temel error handling polish yap.

Backend:
- 400/404/500 response mesajları anlaşılır olsun.
- FastAPI hata verirse NestJS anlamlı response dönsün.
- Publish sadece approved fact için çalışsın.

Frontend:
- API error mesajları toast veya alert olarak görünsün.
- Loading state'ler eklensin.
- Empty state'ler eklensin.

Gereksiz yeni dependency ekleme.
Commit atma.
```

---

## Task 9.4 - README local setup güncellemesi

### Amaç

Projeyi baştan sona çalıştırmak için net komutlar yazmak.

### Kabul kriteri

```text
README ile yeni bir geliştirici projeyi çalıştırabilir.
```

### İçerik

```text
1. Requirements
2. docker compose up
3. apps/api setup
4. apps/ai-api setup
5. apps/web setup
6. Migration
7. Mock data upload
8. Demo flow
9. Troubleshooting
```

### Codex prompt

```text
Root README.md dosyasını kapsamlı local setup rehberiyle güncelle.

İçerik:
- Requirements: Node, npm, Python, Docker
- docker compose up -d postgres neo4j
- apps/api npm install, prisma migrate, start:dev
- apps/ai-api venv, pip install, uvicorn
- apps/web npm install, npm run dev
- .env.example dosyalarının nasıl kopyalanacağı
- Mock data upload akışı
- Demo flow:
  1. Document upload
  2. Extract
  3. Candidate facts review
  4. Approve
  5. Publish
  6. Graph viewer
  7. Ask
- Troubleshooting:
  PostgreSQL connection
  Neo4j auth
  FastAPI not reachable
  LLM env missing

Commit atma.
```

---

## Task 9.5 - Manual smoke test checklist

### Amaç

Demo öncesi elle test edilecek listeyi oluşturmak.

### Dosya

```text
docs/smoke-test-checklist.md
```

### Kabul kriteri

```text
Demo öncesi adım adım kontrol listesi var.
```

### Codex prompt

```text
docs/smoke-test-checklist.md dosyasını oluştur.

Checklist:
- Docker servisleri çalışıyor mu?
- API health ok mu?
- AI API health ok mu?
- Web açılıyor mu?
- PDF upload çalışıyor mu?
- TXT upload çalışıyor mu?
- MD upload çalışıyor mu?
- Extract çalışıyor mu?
- Evidence atoms oluşuyor mu?
- Candidate facts oluşuyor mu?
- Approve/reject çalışıyor mu?
- Publish çalışıyor mu?
- Neo4j Browser'da graph görünüyor mu?
- Frontend graph viewer çalışıyor mu?
- Ask ekranı örnek sorulara cevap veriyor mu?

Her madde için expected result yaz.

Commit atma.
```

---

# 10. Codex task yürütme sırası

Aşağıdaki sıra önerilir:

```text
0.1 Proje kapsam dokümanları
0.2 Demo ontology
1.1 Monorepo iskeleti
1.2 Docker Compose PostgreSQL + Neo4j
1.3 Next.js app
1.4 NestJS app
1.5 FastAPI app
2.1 Prisma setup
2.2 Document model/module
2.3 File upload
2.4 EvidenceAtom model
2.5 CandidateFact model
3.1 FastAPI schemas
3.2 Text extraction
3.3 Evidence atom generator
3.4 /process-document atoms only
4.1 LLM client
4.2 Fact extraction service
4.3 /process-document atoms + facts
4.4 NestJS extract integration
5.1 Frontend API client/layout
5.2 Upload screen
5.3 Documents list/extract
5.4 Document detail
6.1 Candidate facts list
6.2 Fact detail/edit
6.3 Approve/reject
7.1 Neo4j service
7.2 Publish endpoint
7.3 Graph API
7.4 Graph viewer
8.1 Ask intent parser
8.2 Ask Cypher templates
8.3 Ask UI
9.1 Mock data placement
9.2 Mock upload script
9.3 Error handling polish
9.4 README setup
9.5 Smoke test checklist
```

---

# 11. Önerilen commit grupları

Codex commit atmayacak. Kullanıcı manuel commit atacak.

Önerilen commit mesajları:

```text
docs: define mini kg demo scope
chore: initialize monorepo structure
chore: add postgres and neo4j compose setup
feat(web): initialize nextjs app
feat(api): initialize nestjs api
feat(ai): initialize fastapi service
feat(api): add document upload module
feat(api): add evidence atom and candidate fact models
feat(ai): add document parsing and evidence atom generation
feat(ai): add llm fact extraction
feat(api): integrate document extraction workflow
feat(web): add document upload and list screens
feat(web): add candidate fact review screen
feat(api): add neo4j graph publishing
feat(web): add graph viewer
feat(api): add basic ask endpoint
feat(web): add ask screen
docs: add local setup and smoke test checklist
```

---

# 12. Ana kalite kapıları

Her büyük faz sonunda şu kontroller yapılmalı:

## Faz 1 sonunda

```text
docker compose up -d postgres neo4j
apps/web çalışıyor
apps/api /health çalışıyor
apps/ai-api /health çalışıyor
```

## Faz 2 sonunda

```text
PDF/TXT/MD upload çalışıyor
documents list çalışıyor
Prisma migration çalışıyor
```

## Faz 3 sonunda

```text
FastAPI /process-document atoms döndürüyor
PDF text çıkarılıyor
TXT/MD okunuyor
```

## Faz 4 sonunda

```text
Candidate facts oluşuyor
approval_score var
valid_from/valid_until var
evidence_atom_ids var
```

## Faz 6 sonunda

```text
Candidate facts UI'da görünüyor
Approve/reject/edit çalışıyor
```

## Faz 7 sonunda

```text
Approved facts Neo4j'ye publish ediliyor
Graph viewer çalışıyor
```

## Faz 8 sonunda

```text
Ask ekranı 5+ template soruya cevap veriyor
Evidence ve score cevapta görünüyor
```

---

# 13. En önemli mimari sınırlar

Bu maddeler bozulmamalı:

```text
LLM output → candidate_facts
candidate_facts → human approval
approved facts → Neo4j publish
```

FastAPI doğrudan DB sahibi olmamalı:

```text
Doğru:
NestJS → FastAPI → JSON
NestJS → PostgreSQL
NestJS → Neo4j

Yanlış:
FastAPI → PostgreSQL
FastAPI → Neo4j
```

Frontend doğrudan FastAPI veya Neo4j ile konuşmamalı:

```text
Doğru:
Next.js → NestJS

Yanlış:
Next.js → FastAPI
Next.js → Neo4j
```

---

# 14. İlk Codex başlangıç prompt'u

Projeye sıfırdan başlarken Codex'e şu prompt verilebilir:

```text
Bu repo Singularity Mini KG Demo projesidir.

Amaç:
PDF/TXT/MD dosyalarından evidence atom üretmek, LLM ile candidate facts çıkarmak, her fact için approval_score ve valid_from/valid_until tutmak, kullanıcı onayı sonrası fact'leri Neo4j knowledge graph'a publish etmek ve frontend'de graph viewer + basic ask ekranı sunmak.

Mimari:
- apps/web: Next.js + React + TypeScript + Tailwind + shadcn/ui
- apps/api: NestJS + Prisma + PostgreSQL + Neo4j driver
- apps/ai-api: FastAPI + Pydantic + PDF/TXT/MD parser + LLM extraction
- docker-compose: PostgreSQL + Neo4j
- packages/contracts: ortak JSON schema
- packages/ontology: demo ontology

Kurallar:
- Tek seferde tüm projeyi yapma.
- Sadece senden istediğim task'i yap.
- Servisler birbirlerinin iç dosyalarını import etmesin.
- apps/web sadece NestJS API ile konuşsun.
- apps/api FastAPI ile HTTP üzerinden konuşsun.
- FastAPI DB'ye doğrudan yazmasın; structured JSON dönsün.
- LLM çıktısını doğrudan Neo4j'ye yazma.
- Önce candidate_facts tablosuna yaz, sonra approved facts publish edilsin.
- Commit atma; commit'i ben atacağım.
- Her task sonunda çalıştırmam gereken komutları ve kontrol listesini yaz.

Şimdi sadece Task 1.1'i yap:
Monorepo iskeletini oluştur.
```

---

# 15. Task kullanım yöntemi

Her task için Codex'e şu formatta komut ver:

```text
Aşağıdaki task'i uygula.

Task:
[task adı]

Bağlam:
Singularity Mini KG Demo monorepo projesindeyiz.
Mimari sınırlar:
- apps/web sadece apps/api ile konuşur.
- apps/api apps/ai-api ile HTTP üzerinden konuşur.
- apps/ai-api DB'ye doğrudan yazmaz.
- LLM çıktısı doğrudan Neo4j'ye yazılmaz.

Yapılacaklar:
[task yapılacakları]

Kabul kriterleri:
[task kabul kriterleri]

Commit atma.
Sonunda çalıştırmam gereken komutları ve test checklist'ini yaz.
```

---

# 16. Demo tamamlandığında beklenen çıktı

Demo bittiğinde sistem şunu yapabilmeli:

```text
1. Kullanıcı 12 mock dosyayı yükler.
2. Dosyalar PostgreSQL documents tablosuna kaydedilir.
3. Extract işlemi FastAPI ile çalışır.
4. Evidence atoms PostgreSQL'e kaydedilir.
5. LLM candidate facts çıkarır.
6. Candidate facts approval_score ve validity dates taşır.
7. Kullanıcı facts ekranında inceler.
8. Kullanıcı bazı facts'i approve eder.
9. Approved facts Neo4j'ye publish edilir.
10. Graph viewer node/relation gösterir.
11. Edge detayında evidence ve score görünür.
12. Ask ekranı basit soruları graph üzerinden cevaplar.
```

Beklenen demo metrikleri:

```text
Uploaded documents: 12
Evidence atoms: 40-100
Candidate facts: 30-60
Approved facts: 15-30
Graph nodes: 15-40
Graph relations: 15-30
Supported ask templates: 5+
```

---

# 17. Bu task planının amacı

Bu task planı, demo projesini hızlı ama kontrolsüz değil, **küçük adımlarla ve doğru mimari sınırlarla** geliştirmek için hazırlanmıştır.

Bu planla hedeflenen şey:

```text
Atılacak oyuncak demo değil,
ileride ana projeye büyüyebilecek çekirdek sistem.
```


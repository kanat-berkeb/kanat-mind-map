
---

## 1. Genel proje özeti

### 1.1 Proje adı

```text
Singularity Mini KG Demo
```

### 1.2 Kısa tanım

Bu demo; PDF, transcript ve yazılım notlarından evidence atomları üreten, LLM ile candidate fact çıkaran, her fact için approval score ve geçerlilik tarihi tutan, kullanıcı onayı sonrası fact'leri Neo4j knowledge graph'a publish eden ve frontend'de graph viewer + basit ask ekranı sunan küçük bir monorepo uygulamasıdır.

### 1.3 Ana teknoloji stack

```text
Frontend:
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- TanStack Table
- React Hook Form
- Zod
- React Flow

Backend:
- NestJS
- Prisma
- PostgreSQL
- Neo4j Driver

AI Service:
- FastAPI
- Pydantic
- PyMuPDF veya pypdf
- LLM client

Infra:
- Docker Compose
- PostgreSQL
- Neo4j
- Local file storage
```

### 1.4 Demo dışında kalacak teknolojiler

Bu demo aşamasında aşağıdakiler eklenmeyecek:

```text
Qdrant
pgvector
OpenSearch
Kafka
Temporal
RabbitMQ
BullMQ
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

---

## 2. Codex çalışma kuralları

Codex ile her task şu kurallara uymalıdır:

```text
1. Commit atma. Commit'i kullanıcı manuel atacak.
2. Tek task'ta tüm projeyi yapmaya çalışma.
3. Var olan mimariyi bozma.
4. apps/web, apps/api, apps/ai-api sınırlarını koru.
5. apps/web sadece NestJS API ile konuşsun.
6. apps/api FastAPI ile HTTP üzerinden konuşsun.
7. apps/ai-api doğrudan PostgreSQL veya Neo4j'ye yazmasın.
8. LLM çıktısı doğrudan Neo4j'ye yazılmasın.
9. Önce candidate_facts tablosuna yazılsın.
10. Sadece approved facts Neo4j'ye publish edilsin.
11. Her task sonunda çalıştırılacak komutları yaz.
12. Her task sonunda test/kontrol checklist'i yaz.
13. Gereksiz teknoloji ekleme.
14. Yeni dependency eklerken nedenini açıkla.
15. Environment variable'ları .env.example dosyalarına ekle.
```

---

## 3. Hedef monorepo yapısı

```text
singularity-platform/
  README.md
  docker-compose.yml
  .env.example
  .gitignore

  apps/
    web/
      # Next.js frontend
      Dockerfile
      package.json
      src/

    api/
      # NestJS backend
      Dockerfile
      package.json
      prisma/
      src/

    ai-api/
      # FastAPI AI/document service
      Dockerfile
      requirements.txt
      app/

  packages/
    contracts/
      extracted-fact.schema.json
      evidence-atom.schema.json
      graph.schema.json

    ontology/
      demo-ontology.yaml

  mock-data/
    pdf/
    transcripts/
    software-notes/

  docs/
    architecture.md
    demo-plan.md
    evidence-atom-rules.md
    codex-task-plan.md
```

---

## 4. Task fazları

Task'ler şu fazlara bölünmüştür:

```text
Faz 0: Proje hazırlık ve mimari doküman
Faz 1: Monorepo, infra ve temel servisler
Faz 2: NestJS API temel modülleri
Faz 3: FastAPI document processing
Faz 4: Evidence atom ve candidate fact extraction
Faz 5: Frontend temel ekranlar
Faz 6: Human review ve publish
Faz 7: Neo4j graph viewer
Faz 8: Basic ask
Faz 9: Demo polish, seed, test ve dokümantasyon
```

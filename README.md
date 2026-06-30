# Singularity Mini KG Demo

PDF, TXT ve Markdown kaynaklarından evidence atomları ve LLM destekli candidate fact'ler üreten; insan tarafından onaylanan fact'leri Neo4j knowledge graph'a yayımlayan bir monorepo demosudur.

Uçtan uca hedef akış:

```text
Document upload
→ text extraction
→ evidence atom generation
→ candidate fact extraction
→ human review
→ Neo4j publish
→ graph viewer / basic ask
```

## Servisler

- `apps/web`: Next.js tabanlı document, fact review, graph viewer ve basic ask arayüzü.
- `apps/api`: NestJS tabanlı ana API; persistence, workflow, AI servis orchestration ve Neo4j publish katmanı.
- `apps/ai-api`: FastAPI tabanlı document processing ve LLM extraction servisi. Veritabanlarına doğrudan yazmaz.
- `packages/contracts`: Servisler arasında paylaşılacak JSON şemaları.
- `packages/ontology`: İzinli entity ve relation tiplerinin merkezi tanımları.
- `mock-data`: PDF, transcript ve software note demo girdileri.

## Local geliştirme yaklaşımı

Local ortamda PostgreSQL ve Neo4j Docker Compose ile çalışacaktır. Web yalnızca NestJS API'ye; NestJS, FastAPI'ye HTTP üzerinden bağlanacaktır. PostgreSQL operasyonel kayıtların, Neo4j ise yalnızca onaylanıp yayımlanmış fact'lerin veri deposudur.

Uygulama framework kurulumları ve servis çalıştırma komutları sonraki task'lerde eklenecektir.

## Altyapıyı çalıştırma

Docker Engine veya Docker Desktop ile Docker Compose eklentisi kurulu olmalıdır.

Local environment dosyasını oluşturun:

```bash
cp .env.example .env
```

PostgreSQL ve Neo4j servislerini başlatın:

```bash
docker compose up -d postgres neo4j
```

Container durumlarını kontrol edin:

```bash
docker compose ps
```

PostgreSQL `localhost:5432`, Neo4j Browser `http://localhost:7474` ve Neo4j Bolt `bolt://localhost:7687` adresinde çalışır.

## Dokümantasyon

- [Demo planı](docs/demo-plan.md)
- [Mimari](docs/architecture.md)
- [Evidence atom kuralları](docs/evidence-atom-rules.md)
- [Task planı](docs/codex-task-plan.md)

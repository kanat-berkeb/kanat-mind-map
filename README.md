# kanat-mind-map

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

Framework ve container temelleri hazırdır. Living memory yetenekleri `codex-task-sequence.md` sırasıyla, küçük ve doğrulanabilir task'ler halinde eklenecektir.

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

## Tüm servisleri Docker ile çalıştırma

Her uygulama ayrı container olarak çalışır:

- `web`: Next.js, `http://localhost:3000`
- `api`: NestJS, `http://localhost:3001`
- `ai-api`: FastAPI, `http://localhost:8000`
- `postgres`: PostgreSQL, `localhost:5432`
- `neo4j`: Neo4j Browser/Bolt, `localhost:7474` ve `localhost:7687`

Kurumsal TLS inspection için `certs/Fortinet_CA_SSL.crt`, üç uygulama image'ının sistem CA deposuna eklenir. npm ve pip TLS doğrulamasını kapatmadan bu CA deposunu kullanır. Sertifika değişirse image'ları cache kullanmadan yeniden build edin:

```bash
docker compose build --no-cache web api ai-api
```

Tüm image'ları build edip servisleri başlatın:

```bash
docker compose up -d --build
```

Durum ve health kontrolleri:

```bash
docker compose ps
curl http://localhost:3000
curl http://localhost:3001/health
curl http://localhost:8000/health
```

Uygulama logları:

```bash
docker compose logs -f web api ai-api
```

Container'ları durdurun:

```bash
docker compose down
```

## Web uygulamasını çalıştırma

```bash
cd apps/web
npm install
npm run dev
```

Web uygulaması `http://localhost:3000` adresinde açılır.

## API uygulamasını çalıştırma

```bash
cd apps/api
npm install
npm run start:dev
```

API varsayılan olarak `http://localhost:3001` adresinde çalışır. Health kontrolü:

```bash
curl http://localhost:3001/health
```

Beklenen response:

```json
{"status":"ok"}
```

## AI API uygulamasını çalıştırma

```bash
cd apps/ai-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

AI API `http://localhost:8000` adresinde çalışır. Health kontrolü:

```bash
curl http://localhost:8000/health
```

Beklenen response:

```json
{"status":"ok"}
```

## Dokümantasyon

- [Demo planı](docs/demo-plan.md)
- [Mimari](docs/architecture.md)
- [Evidence atom kuralları](docs/evidence-atom-rules.md)
- [Task planı](docs/codex-task-plan.md)

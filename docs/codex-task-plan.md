# Singularity Mini KG Codex Task Planı

## Çalışma yöntemi

Task'ler aşağıdaki sırayla, tek tek uygulanır. Her task mevcut mimariyi korumalı, gereksiz dependency eklememeli, ilgili test veya manuel kontrolü belirtmeli ve commit oluşturmamalıdır. Bir task'ın kabul kriteri sağlanmadan bağımlı sonraki task'a geçilmez.

Değişmez sınırlar:

```text
Next.js → NestJS
NestJS → FastAPI → structured JSON
NestJS → PostgreSQL
NestJS → Neo4j

LLM output → candidate_facts → human approval → Neo4j publish
```

FastAPI'nin PostgreSQL/Neo4j'ye, Next.js'in FastAPI/Neo4j'ye doğrudan erişmesi yasaktır.

## Faz 0 — Hazırlık

- **0.1 Proje kapsam dokümanları:** `docs/demo-plan.md`, `docs/architecture.md`, `docs/evidence-atom-rules.md` ve bu task planını oluştur.
- **0.2 Demo ontology:** İzinli entity ve relation tiplerini `packages/ontology/demo-ontology.yaml` içinde tanımla.

## Faz 1 — Monorepo, altyapı ve servis iskeletleri

- **1.1 Monorepo iskeleti:** `apps/web`, `apps/api`, `apps/ai-api`, `packages/contracts`, `packages/ontology` ve mock-data dizinlerini oluştur.
- **1.2 Docker Compose:** PostgreSQL ve Neo4j servislerini, volume ve env örneklerini ekle.
- **1.3 Next.js app:** TypeScript ve Tailwind tabanlı web uygulamasını başlat.
- **1.4 NestJS app:** API uygulamasını ve `GET /health` endpoint'ini başlat.
- **1.5 FastAPI app:** AI/document servisini ve `GET /health` endpoint'ini başlat.

Kalite kapısı: PostgreSQL ve Neo4j container'ları; üç uygulama ve iki health endpoint'i yerelde çalışır.

## Faz 2 — NestJS veri modelleri ve upload

- **2.1 Prisma setup:** NestJS-Prisma-PostgreSQL bağlantısını ve migration akışını kur.
- **2.2 Document module:** Document modelini ve list/detail endpoint'lerini ekle.
- **2.3 File upload:** `.pdf`, `.txt`, `.md` upload, local storage ve dosya tipi validation ekle.
- **2.4 EvidenceAtom model:** Document relation'ı ve evidence atom listeleme endpoint'ini ekle.
- **2.5 CandidateFact model:** Candidate fact modeli, list/detail/edit/approve/reject endpoint'lerini ekle.

Kalite kapısı: Desteklenen dosyalar yüklenir, document kaydı oluşur, migration'lar temiz veritabanında çalışır.

## Faz 3 — FastAPI document processing

- **3.1 Parser schema'ları:** Request, evidence atom, extracted fact ve response Pydantic modellerini ekle.
- **3.2 Text extraction:** PDF için PyMuPDF veya pypdf; TXT/MD için UTF-8 direct read uygula.
- **3.3 Evidence atom generator:** Kaynak türüne özel bölme, stabil ID ve quality score üretimini uygula.
- **3.4 Process endpoint:** `POST /process-document` ile atoms döndür; candidate facts bu aşamada boş olabilir.

Kalite kapısı: PDF/TXT/MD parse edilir ve endpoint doğrulanmış evidence atom listesi döndürür.

## Faz 4 — LLM candidate fact extraction

- **4.1 LLM client abstraction:** OpenAI-compatible, env ile yapılandırılan ve JSON dönen client ekle.
- **4.2 Extraction ve ontology validation:** Atomları batch'le, izinli ontology ile prompt oluştur, çıktıyı Pydantic ile doğrula.
- **4.3 Process endpoint facts:** Evidence atoms ile candidate facts'i birlikte döndür; LLM yoksa kontrollü warning ver.
- **4.4 NestJS entegrasyonu:** `POST /documents/:id/extract` ile FastAPI'yi çağır, atoms/facts'i PostgreSQL'e yaz ve document durumunu güncelle.

Her fact mevcut `evidence_atom_ids`, 0-1 arası `llm_confidence`, `round(llm_confidence * 100)` değerinde `approval_score`, nullable `valid_from` ve `valid_until` taşır.

Kalite kapısı: Extraction sonunda evidence atomlar ve candidate fact'ler PostgreSQL'de izlenebilir biçimde bulunur.

## Faz 5 — Frontend temel ekranları

- **5.1 API client ve layout:** Merkezi NestJS API client, navigation ve temel state yönetimini kur.
- **5.2 Upload ekranı:** Dosya ve source type alanlarıyla document upload formunu ekle.
- **5.3 Document list:** Tablo, status ve extract aksiyonunu ekle.
- **5.4 Document detail:** Metadata, evidence atoms ve candidate facts görünümünü ekle.

## Faz 6 — Human review

- **6.1 Candidate facts list:** Subject-predicate-object, score, status ve validity sütunlarını sun.
- **6.2 Fact edit:** Fact alanlarını evidence ile birlikte drawer/dialog içinde düzenlenebilir yap.
- **6.3 Approve/reject:** Review aksiyonlarını API ile bağla ve UI state'ini güncelle.

Kalite kapısı: Kullanıcı candidate fact'i evidence ile inceleyebilir, düzenleyebilir, onaylayabilir veya reddedebilir.

## Faz 7 — Neo4j publish ve graph viewer

- **7.1 Neo4j service:** Env tabanlı driver, query helper, lifecycle close ve health kontrolü ekle.
- **7.2 Publish endpoint:** Yalnızca approved fact için node/relation `MERGE` et; relation metadata'sını ve PostgreSQL publish durumunu güncelle.
- **7.3 Graph endpoint:** Published graph'ı `{nodes, edges}` formatında döndür.
- **7.4 Graph viewer:** React Flow ile node/relation ve edge evidence/score detaylarını göster.

Kalite kapısı: Candidate/rejected fact publish edilemez; approved fact idempotent olarak yayımlanır ve viewer'da görünür.

## Faz 8 — Basic ask

- **8.1 Intent parser:** Desteklenen soru kalıplarını basit string matching ile intent ve entity adına ayır.
- **8.2 Cypher templates:** Yedi desteklenen intent için güvenli template query'ler ve evidence içeren response ekle.
- **8.3 Ask ekranı:** Soru input'u, örnekler, loading/error ve evidence/matches görünümünü ekle.

Desteklenen başlangıç intent'leri: müşteri sorumlusu, bölgesi, hedefi ve riskleri; servisin projesi, bağımlılığı ve sahibi.

Kalite kapısı: En az beş örnek soru graph verisinden answer, evidence ve approval score döndürür.

## Faz 9 — Demo polish, seed ve doğrulama

- **9.1 Mock data:** PDF, transcript ve software note örneklerini yerleştir.
- **9.2 Seed/import helper:** Tekrarlanabilir demo veri hazırlama akışı ekle.
- **9.3 Validation/error polish:** Desteklenmeyen input, servis hatası ve boş state'leri anlaşılır hale getir.
- **9.4 README local setup:** Infra, migration ve üç uygulamanın başlatılma sırasını dokümante et.
- **9.5 Manual smoke test:** Upload'dan ask cevabına kadar kontrol listesini ekle.

Kalite kapısı: Temiz yerel ortamda README izlenerek kurulum yapılır ve smoke test baştan sona geçer.

## Her task sonunda kontrol

1. Yalnızca istenen task kapsamı değişti mi?
2. Mimari servis sınırları korundu mu?
3. Eklenen dependency ve env değişkenleri dokümante edildi mi?
4. İlgili test, lint, build veya manuel kontrol çalıştırıldı mı?
5. Kabul kriterlerinin her biri doğrulandı mı?
6. Kullanıcının manuel çalıştıracağı komutlar ve kontrol listesi belirtildi mi?
7. Commit oluşturulmadı mı?

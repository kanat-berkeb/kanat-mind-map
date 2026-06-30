# Codex Task Plan

## Amaç ve yetki sırası

Bu dosya `kanat-mind-map` living memory MVP geliştirme sırasının kısa özetidir.

Task uygulanırken kaynak önceliği:

1. Root `AGENTS.md`: değişmez mimari ve çalışma kuralları
2. Root `codex-task-sequence.md`: ayrıntılı task sırası, kapsam ve kabul kriterleri
3. İlgili `docs/` dosyaları: domain ve teknik gereksinimler
4. Bu dosya: faz özeti

Task numarası veya kapsam çelişirse root `codex-task-sequence.md` esas alınır.

## FAZ 0 — Doküman ve ajan kuralları

- **Task 0.1:** Yeni doküman setini repo'ya yerleştir.
- **Task 0.2:** Root `AGENTS.md` dosyasını ekle.
- **Task 0.3:** Kod değiştirmeden mevcut repo durumunu analiz et.

Kalite kapısı: Living memory dokümanları, ajan kuralları ve mevcut durum raporu tamamlanmış olmalı.

## FAZ 1 — Ontology ve contracts

- **Task 1.1:** Demo ontology dosyasını living memory mimarisine göre güncelle.
- **Task 1.2:** Servis sınırı contract dosyalarını oluştur veya genişlet.

Kalite kapısı: Ontology versioned ve parse edilebilir; contract alanları camelCase ve dokümanlarla uyumlu olmalı.

## FAZ 2 — PostgreSQL data model

- **Task 2.1:** Prisma status enumlarını ve temel lifecycle alanlarını ekle.
- **Task 2.2:** `ValidationResult` ve `ReviewDecision` modellerini ekle.
- **Task 2.3:** `ConflictRecord`, `GraphPatch`, `PublishedAssertion` ve `SemanticMemoryItem` modellerini ekle.

Kalite kapısı: Prisma validation ve migration başarılı; mevcut veri geriye uyumlu kalmalı.

## FAZ 3 — FastAPI schema ve extraction contract uyumu

- **Task 3.1:** FastAPI response schema'larını contracts ile uyumlu hale getir.
- **Task 3.2:** Evidence atom generator'ı yeni kurallara göre sıkılaştır.
- **Task 3.3:** Fact extraction promptunu ontology-aware ve evidence-bound hale getir.

Kalite kapısı: FastAPI stateless kalmalı; response camelCase contract ve evidence kurallarına uymalı.

## FAZ 4 — NestJS extraction ve persistence

- **Task 4.1:** Extract endpoint'ini yeni `ProcessDocumentResponse` contract'ına uyarla.
- **Task 4.2:** Document detail için evidence atom ve candidate fact endpointlerini uyumlu hale getir.

Kalite kapısı: NestJS veri sahibi kalmalı; FastAPI sonuçları doğrulanıp PostgreSQL'e yazılmalı.

## FAZ 5 — Validation Engine

- **Task 5.1:** `ValidationService` skeleton ve check result formatını oluştur.
- **Task 5.2:** Ontology validation ekle.
- **Task 5.3:** Evidence support validation temelini ekle.

Kalite kapısı: Validation sonuçları persisted ve review akışı için izlenebilir olmalı.

## FAZ 6 — Review ve conflict yönetimi

- **Task 6.1:** `ReviewDecision` endpointlerini lifecycle alanlarına göre güncelle.
- **Task 6.2:** Conflict detection temelini ekle.

Kalite kapısı: Kritik bilgi auto-publish edilmemeli; karar ve conflict kayıtları audit edilebilmeli.

## FAZ 7 — Graph Patch ve publish akışı

- **Task 7.1:** `GraphPatchService` skeleton oluştur.
- **Task 7.2:** Publish endpointini GraphPatch akışına taşı.
- **Task 7.3:** Expire ve supersede operasyonlarının temelini ekle.

Kalite kapısı: Yalnız approved patch Curated KG'yi güncelleyebilmeli; publish idempotent olmalı.

## FAZ 8 — Semantic Memory

- **Task 8.1:** `SemanticMemoryService` skeleton oluştur.
- **Task 8.2:** Publish sonrası semantic memory refresh ekle.
- **Task 8.3:** Semantic memory API endpointlerini ekle.

Kalite kapısı: Memory yalnız PublishedAssertion/Curated KG temelinden türetilmeli ve evidence refs taşımalı.

## FAZ 9 — Ask / Working Memory

- **Task 9.1:** `WorkingMemoryBuilder` oluştur.
- **Task 9.2:** Ask endpointini Semantic Memory first hale getir.

Kalite kapısı: LLM'e yalnız görevle ilgili küçük context pack verilmeli; cevap evidence-linked olmalı.

## FAZ 10 — Frontend

- **Task 10.1:** Candidate facts ekranını lifecycle alanlarıyla güncelle.
- **Task 10.2:** Validation result detail UI ekle.
- **Task 10.3:** Graph patch review/list ekranı ekle.
- **Task 10.4:** Semantic memory ekranı ekle.
- **Task 10.5:** Ask ekranında evidence ve memory source göster.

Kalite kapısı: Web yalnız NestJS API ile konuşmalı; candidate, validation, patch ve published state ayrımı görünür olmalı.

## FAZ 11 — Seed, smoke test ve dokümantasyon

- **Task 11.1:** Mock data ve expected output'ları düzenle.
- **Task 11.2:** README local setup ve demo flow bilgisini güncelle.
- **Task 11.3:** Smoke test checklist'ini yeni akışa göre güncelle.

Kalite kapısı: Temiz ortamda kurulum ve upload → evidence → candidate → validation → review → patch → publish → memory → ask akışı doğrulanmalı.

## Her task sonunda

- Değişen dosyaları listele.
- Çalıştırılan ve kullanıcıya bırakılan komutları yaz.
- Manuel kontrol checklist'i ver.
- Yeni dependency/env ve bilinen riskleri açıkla.
- Commit atma; commit kullanıcı tarafından yapılır.

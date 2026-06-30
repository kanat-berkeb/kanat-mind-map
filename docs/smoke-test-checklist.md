# Smoke Test Checklist

## 1. Amaç

Bu checklist, demo öncesi `kanat-mind-map` akışının baştan sona çalıştığını manuel olarak doğrulamak için kullanılır.

## 2. Infra

- [ ] Docker çalışıyor.
  - Beklenen: `docker ps` hata vermiyor.

- [ ] PostgreSQL container çalışıyor.
  - Beklenen: API migration bağlantı kurabiliyor.

- [ ] Neo4j container çalışıyor.
  - Beklenen: Neo4j Browser açılıyor veya API Neo4j health check başarılı.

## 3. Servis health

- [ ] NestJS API health çalışıyor.
  - Beklenen: `GET /health` başarılı.

- [ ] FastAPI health çalışıyor.
  - Beklenen: `GET /health` başarılı.

- [ ] Next.js web açılıyor.
  - Beklenen: Ana sayfa yükleniyor.

## 4. Document upload

- [ ] PDF upload çalışıyor.
  - Beklenen: Document kaydı `uploaded` status ile oluşuyor.

- [ ] TXT upload çalışıyor.
  - Beklenen: Document kaydı oluşuyor.

- [ ] MD upload çalışıyor.
  - Beklenen: Document kaydı oluşuyor.

- [ ] Unsupported file type reddediliyor.
  - Beklenen: 400 response ve anlaşılır hata mesajı.

## 5. Extraction

- [ ] Extract butonu çalışıyor.
  - Beklenen: NestJS FastAPI'yi çağırıyor.

- [ ] Evidence atoms oluşuyor.
  - Beklenen: `GET /documents/:id/evidence-atoms` atom listesi döndürüyor.

- [ ] Candidate facts oluşuyor.
  - Beklenen: `GET /facts/candidates` candidate listesi döndürüyor.

- [ ] LLM env yoksa sistem kırılmıyor.
  - Beklenen: Evidence atoms dönüyor, candidate facts boş ve warning mevcut.

## 6. Validation

- [ ] Candidate fact validate edilebiliyor.
  - Beklenen: ValidationResult oluşuyor.

- [ ] Ontology dışı relation warning/fail üretiyor.
  - Beklenen: Validation check failed veya warning.

- [ ] Evidence olmayan fact geçersiz.
  - Beklenen: evidence support validation failed.

## 7. Review

- [ ] Candidate fact detayında evidence görünüyor.
  - Beklenen: Evidence text ve atom refs görünür.

- [ ] Approve çalışıyor.
  - Beklenen: reviewStatus `approved` olur.

- [ ] Reject çalışıyor.
  - Beklenen: reviewStatus `rejected` olur.

## 8. Graph patch

- [ ] Approved candidate için graph patch oluşturulabiliyor.
  - Beklenen: GraphPatch kaydı oluşur.

- [ ] Patch operations görüntüleniyor.
  - Beklenen: ADD_ASSERTION / EXPIRE_ASSERTION gibi operation'lar görünür.

- [ ] Rejected patch publish edilemiyor.
  - Beklenen: 400/403 response.

## 9. Publish

- [ ] Approved patch Neo4j'ye publish ediliyor.
  - Beklenen: Neo4j'de node/relation oluşur.

- [ ] Publish idempotent.
  - Beklenen: Aynı patch ikinci kez duplicate relation üretmez.

- [ ] PublishedAssertion kaydı oluşuyor.
  - Beklenen: PostgreSQL audit kaydı var.

## 10. Semantic memory

- [ ] Publish sonrası semantic memory güncelleniyor.
  - Beklenen: SemanticMemoryItem oluşur veya version artar.

- [ ] Memory card frontend'de görünür.
  - Beklenen: summary, current facts, evidence refs görünür.

## 11. Ask

- [ ] Basic ask çalışıyor.
  - Beklenen: Desteklenen soru cevap döner.

- [ ] Cevap evidence içeriyor.
  - Beklenen: evidenceText veya evidenceAtomIds görünür.

- [ ] Current vs historical ayrımı çalışıyor.
  - Beklenen: Güncel soru active fact'ten, geçmiş soru historical fact'ten cevaplanır.

## 12. Ayşe / Mehmet senaryosu

- [ ] İlk doküman Ayşe satış başkanı bilgisini üretir.
  - Beklenen: Ayşe role assignment active olabilir.

- [ ] İkinci doküman Mehmet satış başkanı, Ayşe yardımcısı bilgisini üretir.
  - Beklenen: Validation cardinality conflict veya role transition önerir.

- [ ] Patch Ayşe'yi expired, Mehmet'i active yapar.
  - Beklenen: Curated KG ve semantic memory güncellenir.

## 13. Demo tamamlandı kriteri

Tüm temel akış şu şekilde çalışıyorsa demo hazırdır:

```text
Upload
→ Extract
→ Evidence Atoms
→ Candidate Facts
→ Validation
→ Review
→ Graph Patch
→ Publish
→ Semantic Memory
→ Ask with Evidence
```

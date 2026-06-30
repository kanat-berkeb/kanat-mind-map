# MVP Demo Plan

## 1. Amaç

Bu MVP, `kanat-mind-map` projesinin temel bilgi üretim hattını kanıtlar.

Eski mini demo akışı:

```text
Upload
→ Evidence Atom
→ Candidate Fact
→ Human Review
→ Neo4j Publish
→ Graph Viewer
→ Basic Ask
```

Yeni MVP akışı:

```text
Upload
→ Evidence Archive
→ Evidence Atom
→ Candidate Knowledge
→ Validation
→ Human Review
→ Graph Patch
→ Curated KG
→ Semantic Memory
→ Working Memory
→ Basic Ask
```

Bu fark önemlidir. Artık LLM çıktısı doğrudan graph'a yazılmaz. Önce candidate bilgi olur, validation'dan geçer, graph patch'e dönüşür, insan/policy onayından sonra curated KG'ye yazılır ve semantic memory bundan türetilir.

## 2. Demo kapsamı

MVP şu yetenekleri kapsar:

```text
PDF/TXT/MD upload
source metadata tutma
file parsing
evidence atom generation
candidate fact extraction
ontology validation
validation result kaydı
human review
conflict detection temel seviyesi
graph patch proposal
approved patch publish
curated KG graph viewer
semantic memory card generation
basic ask with evidence
fact lifecycle yönetimi
```

## 3. Demo dışı

Bu aşamada bilinçli olarak dışarıda bırakılır:

```text
production IAM
advanced vector retrieval
OpenSearch/Qdrant/pgvector
Kafka/Temporal/RabbitMQ
MinIO/S3
LangGraph/LlamaIndex/Ragas
Prometheus/Grafana/Sentry
full ontology migration engine
production-grade ACL policy engine
free-form general QA over all company data
```

## 4. Ana kullanıcı akışı

1. Kullanıcı PDF/TXT/MD dosyası yükler.
2. NestJS dosyayı local storage'a kaydeder ve `Document` kaydı oluşturur.
3. Kullanıcı extraction başlatır.
4. NestJS, FastAPI `/process-document` endpoint'ini çağırır.
5. FastAPI dokümanı parse eder ve evidence atom üretir.
6. FastAPI LLM/agent ile candidate facts çıkarır.
7. NestJS atoms ve candidate facts'i PostgreSQL'e yazar.
8. Validation engine candidate facts'i kontrol eder.
9. Uygun candidate'lar graph patch proposal'a dönüştürülür.
10. Kullanıcı review ekranında patch/fact/evidence üçlüsünü inceler.
11. Onaylanan patch Curated KG'ye publish edilir.
12. Curated KG update event'i Semantic Memory Builder'ı tetikler.
13. Semantic memory kartları güncellenir.
14. Kullanıcı Graph Viewer veya Ask ekranından sorgular.

## 5. Başarı kriterleri

Demo sonunda şu akış baştan sona çalışmalıdır:

```text
Upload → Extract → Evidence Atoms → Candidate Facts → Validation → Review → Graph Patch → Publish → Semantic Memory → Ask
```

Ölçülebilir hedefler:

```text
5-12 mock doküman yüklenebilmeli.
40-120 evidence atom üretilebilmeli.
25-80 candidate fact çıkarılabilmeli.
10-40 fact review edilebilmeli.
10-30 assertion curated KG'ye publish edilebilmeli.
5-15 semantic memory card üretilebilmeli.
Basic ask en az 5 soru tipine evidence'lı cevap dönebilmeli.
```

Bu sayılar performans taahhüdü değil, demo veri yeterlilik ölçütüdür.

## 6. MVP'de gerekli ekranlar

```text
Documents
Document Detail
Evidence Atoms
Candidate Facts
Validation Results
Review Queue
Graph Patch Detail
Curated Graph Viewer
Semantic Memory Cards
Ask
```

## 7. MVP'de desteklenen soru tipleri

```text
X kimden sorumlu?
X hangi bölgede?
X hedefi ne?
X riskleri neler?
X hangi projenin parçası?
X hangi servise bağımlı?
X'in sahibi kim?
Bu bilginin kaynağı ne?
```

## 8. Tamamlanma tanımı

MVP şu koşullarda tamamlanmış sayılır:

```text
Temiz ortamda README izlenerek servisler ayağa kalkar.
Document upload çalışır.
Extraction evidence atoms ve candidate facts üretir.
Validation sonuçları görülebilir.
Review approve/reject çalışır.
Approved patch Neo4j'ye idempotent publish edilir.
SemanticMemoryItem üretilir.
Ask endpoint semantic memory first, KG fallback mantığıyla cevap verir.
Cevaplarda evidence ve approval bilgisi görünür.
```

# CandidateFact Lifecycle Migration Plan

Repo'da Task 2.1 öncesinde Prisma schema veya migration bulunmadığı için ilk
migration `CandidateFact` tablosunu ve üç lifecycle enumunu sıfırdan oluşturur.

## Yeni kurulum

Henüz migration oluşturulmadıysa PostgreSQL çalışırken `apps/api` içinde güncel
schema'nın tamamı için:

```bash
npx prisma migrate dev --name add_living_memory_workflow_models
npx prisma generate
```

Task 2.1 migration'ı daha önce uygulanmış bir veritabanında yalnız Task 2.2
tablolarını eklemek için:

```bash
npx prisma migrate dev --name add_validation_and_review_models
npx prisma generate
```

`ValidationResult` ve `ReviewDecision` yeni tablolar olduğu için mevcut
`CandidateFact` satırlarına backfill gerekmez. Foreign key'ler zorunludur.
Validation ve review geçmişini korumak için bağlı kayıt varken parent candidate
silinmesi `ON DELETE RESTRICT` ile engellenir.

## Task 2.3 tabloları

Task 2.1 ve 2.2 migration'ları daha önce uygulanmış bir veritabanında:

```bash
npx prisma migrate dev --name add_graph_patch_and_memory_models
npx prisma generate
```

`ConflictRecord`, `GraphPatch`, `PublishedAssertion` ve `SemanticMemoryItem` yeni
tablolardır; mevcut satırlara backfill gerekmez. `PublishedAssertion` bağlıyken
`GraphPatch` silinemez. `SemanticMemoryItem`, `CandidateFact` ile relation taşımaz;
`generatedFrom` yalnız curated graph veya published assertion kaynaklarını kabul
eder.

## Harici legacy tablo varsa

Migration çalıştırılmadan önce tablo introspect edilmeli ve mevcut tek `status`
alanı korunmalıdır. Geçiş sırası:

1. Yeni enum tipleri ve nullable/default değerli lifecycle kolonlarını ekle.
2. Legacy `status` değerlerini üç eksene açık mapping ile backfill et.
3. Uygulama okumalarını yeni alanlara geçir; legacy `status` alanını bu taskta silme.
4. Veri ve uygulama doğrulandıktan sonra ayrı migration ile legacy alanı kaldır.

Varsayılan mapping önerisi:

```text
candidate  -> candidate / unpublished / NULL
approved   -> approved  / unpublished / NULL
rejected   -> rejected  / unpublished / NULL
published  -> approved  / published   / active
expired    -> approved  / published   / expired
retracted  -> approved  / published   / retracted
conflicted -> needs_review / unpublished / conflicted
```

Mapping, üretim verisi görülmeden otomatik uygulanmamalıdır.

## Task 4.1 document extraction tabloları

`Document` ve `EvidenceAtom` tabloları ile `CandidateFact.sourceDocumentId`
foreign key'i eklenir:

```bash
npx prisma migrate dev --name add_document_extraction_persistence
npx prisma generate
```

Legacy `CandidateFact.sourceDocumentId` değerleri gerçek bir `Document.id` ile
eşleşmiyorsa foreign key eklenmeden önce temizlenmeli veya document kayıtlarına
map edilmelidir. Mapping üretim verisi görülmeden otomatik uygulanmamalıdır.

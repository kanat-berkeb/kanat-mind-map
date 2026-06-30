# CandidateFact Lifecycle Migration Plan

Repo'da Task 2.1 öncesinde Prisma schema veya migration bulunmadığı için ilk
migration `CandidateFact` tablosunu ve üç lifecycle enumunu sıfırdan oluşturur.

## Yeni kurulum

PostgreSQL çalışırken `apps/api` içinde:

```bash
npx prisma migrate dev --name add_candidate_fact_lifecycle
npx prisma generate
```

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

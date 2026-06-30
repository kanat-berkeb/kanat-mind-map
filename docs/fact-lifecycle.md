# Fact Lifecycle

## 1. Amaç

Canlı bilgi sisteminde bilgi sadece `var` veya `yok` değildir. Bilgi aday olabilir, onay bekleyebilir, publish edilmiş olabilir, güncel olabilir, eskiyebilir, başka bilgi tarafından ezilebilir veya hatalı olduğu için geri çekilebilir.

Bu doküman fact/assertion lifecycle modelini tanımlar.

## 2. Tek status yerine üç eksen

MVP'de basitlik için tek `status` alanı kullanılabilir. Ancak hedef mimaride status üç ayrı eksene ayrılmalıdır:

```text
reviewStatus       = İnsan/policy review süreci
publicationStatus  = Curated KG'ye publish süreci
validityStatus     = Gerçek dünyadaki geçerlilik durumu
```

Önerilen alanlar:

```json
{
  "reviewStatus": "approved",
  "publicationStatus": "published",
  "validityStatus": "active"
}
```

Bu ayrım karışıklığı önler.

## 3. Review status

| Status | Anlam |
|---|---|
| `candidate` | LLM/agent çıkardı, henüz güvenilir değil |
| `validated` | Otomatik kontrolleri geçti |
| `needs_review` | İnsan incelemesi gerekiyor |
| `approved` | İnsan veya policy tarafından onaylandı |
| `rejected` | Reddedildi |

## 4. Publication status

| Status | Anlam |
|---|---|
| `unpublished` | Curated KG'ye yazılmadı |
| `publish_pending` | Publish kuyruğunda |
| `published` | Curated KG'ye yazıldı |
| `publish_failed` | Publish sırasında hata oluştu |

## 5. Validity status

| Status | Anlam |
|---|---|
| `active` | Güncel geçerli bilgi |
| `expired` | Eskiden geçerliydi, artık değil |
| `superseded` | Yeni bilgi bunun yerini aldı |
| `retracted` | Hatalı olduğu için geri çekildi |
| `conflicted` | Çelişkili, karar bekliyor |
| `unknown` | Geçerlilik durumu belirsiz |

## 6. Neden eski bilgi silinmez?

Yanlış yaklaşım:

```text
Eski fact'i sil, yenisini yaz.
```

Doğru yaklaşım:

```text
Eski fact expired/superseded/retracted olur.
Yeni fact active olur.
Aralarındaki ilişki kaydedilir.
```

Bu sayede sistem şu soruları cevaplar:

```text
Şu an ne doğru?
Geçmişte ne doğruydu?
Bu bilgi ne zaman değişti?
Bu bilgi hatalı mıydı, yoksa eskidi mi?
Yeni bilgi hangi eski bilginin yerini aldı?
```

## 7. Expired, superseded, retracted farkı

### expired

Eskiden doğruydu, artık geçerli değil.

Örnek:

```text
Ayşe Ocak-Haziran arasında satış başkanıydı.
Haziran'da görev Mehmet'e geçti.
```

### superseded

Yeni bilgi bunun yerini aldı.

Örnek:

```text
2026 hedef dosyası v2, v1 hedeflerini güncelledi.
```

### retracted

Eski bilgi hatalıydı.

Örnek:

```text
Önceki organizasyon şemasında Ayşe yanlışlıkla satış başkanı yazılmıştır.
Doğru kişi Mehmet'tir.
```

## 8. Ayşe / Mehmet örneği

İlk bilgi:

```text
Ayşe Kaya satış başkanıdır.
```

Yeni bilgi:

```text
Mehmet Demir satış başkanı, Ayşe Kaya satış başkan yardımcısıdır.
```

Graph patch:

```json
{
  "patchId": "patch_role_change_001",
  "changeType": "role_transition",
  "operations": [
    {
      "op": "EXPIRE_ASSERTION",
      "assertionId": "assert_ayse_sales_president",
      "validUntil": "2026-06-15"
    },
    {
      "op": "ADD_ASSERTION",
      "subjectId": "person_mehmet",
      "predicate": "holdsRole",
      "objectId": "role_sales_president",
      "validFrom": "2026-06-15",
      "validityStatus": "active"
    },
    {
      "op": "ADD_ASSERTION",
      "subjectId": "person_ayse",
      "predicate": "holdsRole",
      "objectId": "role_sales_vice_president",
      "validFrom": "2026-06-15",
      "validityStatus": "active"
    }
  ]
}
```

## 9. Bitemporal alanlar

İki zaman ayrı tutulmalıdır:

```text
validTime       = gerçek dünyada geçerli olduğu zaman
transactionTime = sistemin bunu öğrendiği/yazdığı zaman
```

Örnek:

```json
{
  "validFrom": "2026-06-01",
  "knownFrom": "2026-06-15"
}
```

Anlamı:

```text
Mehmet gerçek dünyada 1 Haziran'dan beri satış başkanıdır.
Sistem bunu 15 Haziran'da öğrenmiştir.
```

## 10. State transition özeti

```text
candidate
→ validated
→ needs_review
→ approved
→ publish_pending
→ published + active
→ expired / superseded / retracted / conflicted
```

Rejected path:

```text
candidate / needs_review → rejected
```

Publish failure path:

```text
approved → publish_pending → publish_failed
```

## 11. MVP kararı

MVP'de tek `status` alanı kalabilir ama dokümantasyon ve DTO'lar hedef modeli bilmelidir.

MVP fallback:

```text
candidate
approved
rejected
published
expired
retracted
conflicted
```

Tam mimariye geçerken bu alanlar şuna bölünür:

```text
reviewStatus
publicationStatus
validityStatus
```

# Validation and Review Policy

## 1. Amaç

Bu doküman candidate bilgi curated KG'ye ve semantic memory'ye girmeden önce hangi kontrollerden geçeceğini tanımlar.

Ana akış:

```text
LLM output
→ CandidateFact
→ ValidationResult
→ ReviewDecision veya reject
→ GraphPatch
→ Curated KG
→ Semantic Memory
```

## 2. Validation katmanları

### 2.1 Schema validation

LLM çıktısı beklenen JSON schema'ya uymalıdır.

Fail örneği:

```json
{
  "subject": "ABC Boya",
  "relation": "300 ton"
}
```

Eksikler:

```text
predicate
object.type
evidenceAtomIds
confidence
```

### 2.2 Ontology validation

Relation izinli mi ve domain/range doğru mu kontrol edilir.

Geçersiz:

```text
Customer --managedBy--> Region
```

Çünkü `managedBy` object tipi `Person` veya ilgili ontology'de izinli temsilci tipi olmalıdır.

### 2.3 Relation direction validation

Yanlış:

```text
Ahmet --managedBy--> ABC Boya
```

Doğru:

```text
ABC Boya --managedBy--> Ahmet
```

### 2.4 Entity resolution validation

Sistem aynı entity'nin tekrar açılıp açılmadığını kontrol eder.

Sinyaller:

```text
CRM ID
ERP cari kodu
vergi no
email
telefon
adres
isim benzerliği
human merge history
```

### 2.5 Evidence support validation

Fact'in gösterdiği evidence gerçekten claim'i destekliyor mu kontrol edilir.

Kontroller:

```text
evidenceAtomIds boş değil mi?
evidence atom var mı?
evidenceText atom metniyle uyumlu mu?
quote claim'i destekliyor mu?
sayısal değer atomda geçiyor mu?
yıl/birim atomda geçiyor mu?
```

### 2.6 Temporal validation

Fact'in zaman kapsamı doğru mu kontrol edilir.

Örnek:

```text
SalesTarget için year zorunludur.
RoleAssignment için validFrom önerilir.
validUntil, validFrom'dan önce olamaz.
```

### 2.7 Source authority validation

Hangi kaynak hangi bilgi için daha güvenilir kontrol edilir.

Örnek:

```text
Rol bilgisi için HR/ApprovedOrgChart > toplantı notu.
Müşteri temsilcisi için CRM > PDF.
Satış gerçekleşmesi için ERP > sunum.
```

### 2.8 Conflict validation

Yeni candidate mevcut active assertion ile çelişiyor mu?

Örnek:

```text
Mevcut active: Ayşe satış başkanı.
Yeni candidate: Mehmet satış başkanı.
Rule: SalesPresident maxActiveHolders=1.
Sonuç: role transition veya conflict.
```

### 2.9 ACL validation

Türetilmiş bilgi kaynak bilgisinden daha geniş erişime sahip olamaz.

```text
Raw source ACL
→ Evidence atom ACL
→ Candidate fact ACL
→ Graph patch ACL
→ Published assertion ACL
→ Semantic memory ACL
→ Answer ACL
```

### 2.10 Business rule validation

Domain'e özel kurallar uygulanır.

Örnek:

```text
SalesTarget.amount > 0 olmalı.
SalesTarget.unit zorunlu.
CreditRisk claim finance review ister.
Role change HR review ister.
```

## 3. ValidationResult schema

MVP için önerilen çıktı:

```json
{
  "targetType": "CandidateFact",
  "targetId": "cand_001",
  "overallStatus": "needs_review",
  "severity": "warning",
  "checks": [
    {
      "name": "schema_validation",
      "status": "passed",
      "severity": "info",
      "message": "Candidate fact matches schema."
    },
    {
      "name": "ontology_validation",
      "status": "passed",
      "severity": "info",
      "message": "Relation holdsRole is allowed."
    },
    {
      "name": "cardinality_validation",
      "status": "failed",
      "severity": "warning",
      "message": "Another active SalesPresident exists."
    }
  ],
  "recommendedAction": "create_role_transition_graph_patch",
  "requiresHumanReview": true
}
```

## 4. Validation status değerleri

```text
passed
failed
warning
skipped
needs_review
```

`failed` her zaman reject anlamına gelmez. Bazı failed check'ler graph patch veya human review gerektirir.

## 5. Review politikası

Her candidate insan review'a gitmez.

| Risk | Örnek | Review |
|---|---|---|
| Düşük | CRM'den gelen müşteri bölgesi | Auto-approve mümkün |
| Orta | Müşteri hedefi | Sales Ops review |
| Yüksek | Kredi riski, fiyat, hukuki bilgi | Zorunlu review |
| Çelişkili | İki aktif satış başkanı | Zorunlu review |

## 6. Auto-approve şartları

MVP'de dikkatli kullanılmalıdır.

```text
source authoritative ise
ontology validation passed ise
evidence support passed ise
conflict yoksa
ACL valid ise
fact type low risk ise
```

Bu şartların herhangi biri bozulursa review gerekir.

## 7. Review ekranında gösterilecekler

Reviewer şunları görmelidir:

```text
candidate fact
evidence atom text
source document
ontology rule
validation checks
existing active facts
conflict warning
recommended graph patch
approve/reject/edit actions
```

## 8. Conflict çözümü

Conflict çözümü üç şekilde olabilir:

```text
authoritative source wins
human selected winner
both kept with temporal separation
```

Örnek:

```text
Eski: Ayşe satış başkanı active.
Yeni: Mehmet satış başkanı.
Çözüm: Ayşe expired, Mehmet active.
```

## 9. ReviewDecision schema

```json
{
  "targetType": "GraphPatch",
  "targetId": "patch_001",
  "decision": "approved",
  "reviewerId": "user_001",
  "reviewerTeam": "HR",
  "reason": "Approved based on June organization update.",
  "createdAt": "2026-06-30T10:20:00+03:00"
}
```

## 10. Ana kural

```text
Validation karar vermez, kontrol eder.
Human review kritik kararı verir.
Graph patch değişikliği paketler.
Curated KG sadece onaylı patch ile değişir.
```

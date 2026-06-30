# Evidence Atom Rules

## 1. Amaç

Evidence atom, sistemdeki candidate fact, graph patch ve curated assertion için kaynak kanıt görevi gören küçük, izlenebilir ve anlamı korunmuş bilgi parçasıdır.

Evidence atom:

```text
Yorum yapmaz.
Yeni bilgi üretmez.
LLM özeti değildir.
Memory değildir.
Curated fact değildir.
Sadece kanıt parçasıdır.
```

Her candidate fact en az bir evidence atom referansı taşımak zorundadır.

## 2. Evidence atom ile semantic memory farkı

```text
Evidence atom = kaynak kanıt parçası
Semantic memory = curated KG'den üretilmiş öz bilgi durumu
```

Örnek evidence atom:

```text
Mehmet Demir satış başkanı, Ayşe Kaya satış başkan yardımcısıdır.
```

Örnek semantic memory:

```text
Güncel organizasyon bilgisine göre satış başkanı Mehmet Demir,
satış başkan yardımcısı Ayşe Kaya'dır. Önceki kayıtta Ayşe satış başkanı olarak görünüyordu.
```

## 3. Canonical contract alanları

API contract ve frontend/NestJS tarafında camelCase kullanılır. Python/FastAPI tarafında Pydantic modelleri snake_case kullanabilir ama API çıktısında alias ile camelCase dönmelidir.

Önerilen canonical field isimleri:

```json
{
  "atomId": "org-update-2026:a001",
  "documentId": "doc_001",
  "sourceId": "src_001",
  "sourceVersion": "v1",
  "atomIndex": 1,
  "atomType": "paragraph",
  "sourceType": "pdf",
  "text": "Mehmet Demir satış başkanı, Ayşe Kaya satış başkan yardımcısıdır.",
  "structuredContent": null,
  "location": {
    "page": 1,
    "block": 2
  },
  "sectionPath": ["Organizasyon", "Satış"],
  "parentAtomId": null,
  "qualityScore": 92,
  "contentHash": "sha256:...",
  "accessPolicy": "hr_internal",
  "metadata": {
    "parser": "pdf_parser_v1"
  }
}
```

## 4. Parçalama ilkesi

Atom ne çok büyük ne de çok küçük olmalı.

Kötü atom:

```text
10 sayfalık rapor bölümü
```

Sorun: LLM birçok claim arasında karışır.

Kötü atom:

```text
300 ton
```

Sorun: Kimin hedefi, hangi yıl, hangi kaynak belli değildir.

İyi atom:

```text
ABC Boya'nın 2026 satış hedefi 300 tondur.
```

## 5. Genel parçalama kuralları

```text
Kaynak sırası korunur.
Atom ID deterministik üretilir.
Whitespace normalize edilir ama anlam bozulmaz.
Boş ve parser artığı parçalar atılır.
1500 karakter üstü atomlar cümle sınırından bölünür.
80 karakter altı bağlamsız parçalar komşu context ile birleştirilir.
Başlık, speaker, tablo başlığı ve section context kaybedilmez.
```

80 ve 1500 karakter sınırları mutlak semantik kurallar değil, MVP heuristic'leridir.

## 6. PDF kuralları

```text
Sayfa bazlı metin alınır.
pageNumber korunur.
Paragraf ve boş satır sınırları kullanılır.
Header/footer tekrarları filtrelenebilir.
Tablo parse edilebiliyorsa table_row veya table_cell atom üretilir.
```

PDF'de tablo parse edilemezse atom metadata'sına `parserWarning` eklenmelidir.

## 7. TXT / transcript kuralları

```text
Speaker turn ana sınırdır.
Speaker metadata içinde korunur.
Karar/Aksiyon/Risk/Not blokları ayrı atom yapılır.
Çok kısa cevaplar tek başına kanıt değeri taşımıyorsa komşu context ile bağlanır.
```

## 8. Markdown / software note kuralları

```text
# başlıkları sectionPath oluşturur.
Bullet maddeleri ayrı atom olabilir.
Kod blokları rastgele cümlelere bölünmez.
Başlık tek başına claim taşımıyorsa atom değil context olur.
```

## 9. Quality score

`qualityScore` olgunun doğruluğunu değil, atomun extraction için kullanılabilirliğini ölçer.

Pozitif sinyaller:

```text
tam cümle
açık subject/predicate/object sinyali
kaynak konumu belli
tarih, karar, aksiyon, risk işareti var
tablo satırı structured parse edilmiş
```

Negatif sinyaller:

```text
aşırı kısa ve bağlamsız
bozuk OCR
parser artığı
sadece header/footer
zamirle başlayıp context taşımıyor
```

## 10. Evidence support kuralı

Candidate fact sadece mevcut atom ID'lerine referans verebilir.

Geçersiz:

```json
{
  "subjectName": "ABC Boya",
  "predicate": "hasTarget",
  "objectName": "300 ton",
  "evidenceAtomIds": []
}
```

Geçerli:

```json
{
  "subjectName": "ABC Boya",
  "predicate": "hasTarget",
  "objectName": "300 ton / 2026",
  "evidenceAtomIds": ["sales-targets-2026:a042"],
  "evidenceText": "ABC Boya'nın 2026 satış hedefi 300 tondur."
}
```

## 11. Değişmezlik

Evidence atom metni extraction sonrası değiştirilmemelidir. Kaynak değişirse yeni atom versiyonu üretilir.

```text
Old atom remains.
New source version creates new atoms.
Facts point to the specific atom version they used.
```

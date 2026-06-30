# Evidence Atom Kuralları

## Amaç

Evidence atom, bir candidate fact'in hangi kaynak metne dayandığını gösterecek kadar anlamlı; LLM'e güvenilir bağlam sağlayacak kadar bütünlüklü; review ekranında okunabilecek kadar küçük metin parçasıdır.

Her candidate fact en az bir evidence atom kimliğine referans vermelidir. Evidence atomlar kaynak metni yorumlamaz ve yeni bilgi eklemez.

## Ortak çıktı alanları

Her atom şu alanları taşır:

| Alan | Kural |
|---|---|
| `atom_id` | Doküman içinde stabil ve okunabilir kimlik; örnek `quarterly-report:a001` |
| `atom_index` | Sıfırdan veya birden başlayan, doküman içinde tutarlı sıra numarası |
| `atom_type` | `paragraph`, `speaker_turn`, `decision_block`, `heading`, `bullet` gibi kaynak yapısını anlatan tip |
| `source_type` | `pdf`, `transcript` veya `software_note` |
| `page_number` | PDF için 1 tabanlı sayfa; uygulanmıyorsa `null` |
| `section_path` | Markdown başlık hiyerarşisi; uygulanmıyorsa boş liste |
| `text` | Kaynaktan alınmış, normalize edilmiş fakat anlamı değiştirilmemiş içerik |
| `quality_score` | Basit heuristic ile 0-100 arası kalite skoru |
| `char_start`, `char_end` | Hesaplanabiliyorsa kaynak metindeki karakter aralığı |
| `metadata` | Speaker, dosya adı veya parser bilgisi gibi opsiyonel kaynak metadata'sı |

Persistence katmanında ayrıca atomun `documentId`, opsiyonel `hash` ve oluşturulma zamanı tutulur.

## Genel parçalama kuralları

1. Kaynak sırası korunur; `atom_index` deterministik üretilir.
2. Whitespace normalize edilir, fakat metnin anlamını etkileyen satır yapıları korunur.
3. Boş veya yalnızca biçimlendirme karakterlerinden oluşan parçalar atılır.
4. 1500 karakteri aşan atomlar cümle sınırlarından bölünür. Cümle sınırı bulunamazsa güvenli bir kelime sınırı kullanılır.
5. 80 karakterden kısa, tek başına anlam taşımayan satırlar mümkünse komşu atomla birleştirilir.
6. Başlık, speaker etiketi, karar/aksiyon/risk işareti gibi yapısal bağlam kaybedilmez.
7. Birleştirme veya bölme sonrasında atomlar tekrar sıralanır ve kimlikleri deterministik üretilir.
8. Aynı input ve aynı kurallar aynı `atom_id` dizisini üretmelidir.

80 ve 1500 karakter sınırları mutlak semantik kurallar değil, demo için başlangıç heuristic'leridir. Başlık, kod bloğu veya anlamlı kısa karar gibi kendi başına değer taşıyan parçalar yalnızca kısa olduğu için birleştirilmez.

## PDF kuralları

- Metin sayfa bazlı alınır ve `page_number` korunur.
- Her sayfa boş satır/paragraf sınırlarından bölünür.
- Header, footer veya yalnız sayfa numarası olduğu açıkça belirlenebilen tekrarlar filtrelenebilir.
- 1500 karakter üzerindeki paragraflar cümle bazlı bölünür.
- 80 karakter altındaki bağlamsız satırlar aynı sayfadaki uygun komşuyla birleştirilir.
- Sayfalar arası birleştirme ancak cümlenin sayfa sonunda kesildiği açıkça anlaşılırsa yapılır; her durumda kaynak sayfa bilgisi metadata'da korunur.
- Varsayılan `atom_type` değeri `paragraph` olur.

## Transcript kuralları

- Ana sınır speaker turn'dür; speaker değiştiğinde yeni atom başlar.
- Speaker adı/etiketi `metadata.speaker` içinde korunur.
- `Karar`, `Decision`, `Aksiyon`, `Action`, `Risk` ve `Not/Note` olarak işaretlenmiş bloklar ayrı atom yapılır.
- Karar blokları `decision_block`; aksiyon, risk ve not blokları anlamına uygun tiplerle işaretlenir.
- Bir speaker turn 1500 karakteri geçerse cümle bazlı bölünür; her alt atom aynı speaker metadata'sını taşır.
- Çok kısa yanıtlar (`evet`, `tamam` gibi) tek başına kanıt değeri taşımıyorsa komşu turn ile bağlamlandırılabilir; speaker bilgisi kaybedilmez.

## Markdown / software note kuralları

- ATX (`#`) ve mümkünse setext başlıkları section hiyerarşisini günceller.
- Her atom oluştuğu andaki başlık zincirini `section_path` olarak taşır.
- Paragraflar, bullet maddeleri ve anlamlı teknik cümleler ayrı atom olabilir.
- Her bullet bağımsız anlam taşıyorsa ayrı `bullet` atomudur; yalnızca üst maddesiz anlaşılmıyorsa üst madde bağlamıyla birleştirilir.
- Kod blokları rastgele cümlelere bölünmez. Tek başına fact kaynağı değilse yakınındaki açıklama ile birlikte tutulabilir.
- Başlık metni section context sağlar; yalnızca anlamlı bir ifade/karar içeriyorsa ayrı atom olarak üretilir.

## Quality score heuristic'i

`quality_score`, olgunun doğruluğunu değil atomun extraction için kullanılabilirliğini ölçer. Başlangıç skoru 50 alınarak şu sinyaller uygulanabilir:

- Tam cümle veya açık bir bullet: pozitif
- Subject/nesne ve eylem/relation adayı içeren ifade: pozitif
- Kaynak konumunun (`page_number`, `section_path`, speaker) belirli olması: pozitif
- Karar, aksiyon, risk veya tarih gibi açık işaretler: pozitif
- Aşırı kısa, yalnız başlık niteliğinde veya referansı belirsiz ifade: negatif
- Parser artığı, bozuk karakter oranı veya tekrarlı header/footer: negatif
- Bağlam olmadan zamirle başlayan parça: negatif

Sonuç 0-100 aralığına sınırlandırılır. `quality_score`, `approval_score` değildir ve human review yerine geçmez.

## İzlenebilirlik ve fact bağlantısı

- Fact extraction yalnızca mevcut atom kimliklerine referans verebilir.
- `evidence_atom_ids` boş olan LLM çıktısı geçersiz sayılır.
- `evidence_text`, referans verilen atomların metniyle uyumlu olmalı; yeni bir iddia eklememelidir.
- Atom metni extraction sonrasında değiştirilirse stabil kimlik/hash stratejisi yeniden değerlendirilmelidir.
- Candidate fact'ler önce PostgreSQL'e yazılır; evidence atomlar hiçbir koşulda doğrudan Neo4j publish tetiklemez.

## Örnek

Kaynak:

```text
# CRM Sync

- Servisin sahibi Platform Takımıdır.
- CRM Sync, Customer Data projesinin parçasıdır.
```

Olası atomlar:

```json
[
  {
    "atom_id": "crm-sync:a001",
    "atom_index": 1,
    "atom_type": "bullet",
    "source_type": "software_note",
    "page_number": null,
    "section_path": ["CRM Sync"],
    "text": "Servisin sahibi Platform Takımıdır."
  },
  {
    "atom_id": "crm-sync:a002",
    "atom_index": 2,
    "atom_type": "bullet",
    "source_type": "software_note",
    "page_number": null,
    "section_path": ["CRM Sync"],
    "text": "CRM Sync, Customer Data projesinin parçasıdır."
  }
]
```

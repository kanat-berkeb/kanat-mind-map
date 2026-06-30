# Singularity Mini KG Demo Planı

## Amaç

Singularity Mini KG Demo; PDF, TXT ve Markdown kaynaklarından doğrulanabilir bilgi parçaları çıkaran, bu parçalardan LLM ile aday olgular üreten ve yalnızca insan onayından geçen olguları Neo4j bilgi grafına yayımlayan küçük bir monorepo uygulamasıdır.

Demo aşağıdaki uçtan uca akışı kanıtlar:

```text
PDF/TXT/MD upload
→ metin çıkarma
→ evidence atom üretme
→ LLM ile candidate fact çıkarma
→ insan incelemesi ve onayı
→ approved fact'leri Neo4j'ye publish etme
→ graph viewer ve basic ask
```

## Demo kapsamı

- `.pdf`, `.txt` ve `.md` dosyalarını yerel dosya sistemine yükleme
- Yüklenen dosyaların metadata bilgisini PostgreSQL'de tutma
- PDF metnini sayfa bazlı, TXT ve Markdown metnini doğrudan çıkarma
- Metni kaynağı izlenebilir evidence atomlara bölme
- İzinli ontology içindeki entity ve relation tipleriyle candidate fact üretme
- Her candidate fact için kaynak evidence, `llm_confidence`, `approval_score`, `valid_from` ve `valid_until` tutma
- Candidate fact'leri kullanıcıya listeleme, düzenleme, onaylama veya reddetme
- Yalnızca `approved` durumundaki fact'leri Neo4j'ye yayımlama
- Yayımlanmış node ve relation'ları graph viewer üzerinde gösterme
- Önceden tanımlı soru kalıplarıyla graph üzerinden basic ask sunma

## Ana kullanıcı akışı

1. Kullanıcı bir PDF, TXT veya Markdown dosyası yükler.
2. NestJS API dosyayı yerel depolamaya, metadata kaydını PostgreSQL'e yazar.
3. Kullanıcı extraction işlemini başlatır.
4. NestJS API, dosya yolunu FastAPI servisine gönderir.
5. FastAPI metni çıkarır, evidence atomları ve candidate fact'leri structured JSON olarak döner.
6. NestJS sonuçları PostgreSQL'e kaydeder.
7. Kullanıcı candidate fact'leri evidence ve skorlarıyla inceler; düzenler, onaylar veya reddeder.
8. Onaylanmış fact'ler kullanıcı aksiyonuyla Neo4j'ye yayımlanır.
9. Kullanıcı graph viewer'da yayımlanmış grafı görür veya basic ask ekranında desteklenen sorulardan birini sorar.

## Başarı ölçütleri

Demo tamamlandığında:

- 12 mock doküman yüklenebilmeli.
- Yaklaşık 40-100 evidence atom üretilebilmeli.
- Yaklaşık 30-60 candidate fact çıkarılabilmeli.
- Yaklaşık 15-30 fact onaylanıp yayımlanabilmeli.
- Graph viewer yaklaşık 15-40 node ve 15-30 relation gösterebilmeli.
- Basic ask en az 5 soru kalıbını desteklemeli.
- Graph edge detayında evidence, approval score ve geçerlilik tarihleri görülebilmeli.

Bu sayılar kapasite taahhüdü değil, demo verisinin yeterliliğini ölçen hedef aralıklardır.

## Kapsam dışı

Bu demoda aşağıdaki yetenekler ve teknolojiler bulunmaz:

- Vektör arama ve embedding altyapıları: Qdrant, pgvector
- Arama altyapısı: OpenSearch
- Event streaming ve kuyruklar: Kafka, RabbitMQ, BullMQ
- Workflow orchestration: Temporal, LangGraph
- Kimlik ve politika yönetimi: Keycloak, OPA
- Gelişmiş RAG framework'leri ve değerlendirme: LlamaIndex, Ragas
- LLM observability: Langfuse
- Operasyonel gözlemleme: Prometheus, Grafana, Sentry
- Object storage: MinIO
- Container orchestration: Kubernetes
- Serbest biçimli, genel amaçlı doğal dil sorgulama
- Otomatik publish; insan onayı olmadan hiçbir LLM çıktısı grafa yazılmaz

## Tamamlanma tanımı

Demo, yüklemeden basic ask cevabına kadar ana akış yerel ortamda çalıştığında; servis sınırları korunduğunda; sadece approved fact'ler Neo4j'ye yazıldığında; kurulum ve manuel smoke test adımları dokümante edildiğinde tamamlanmış sayılır.

# Memory Taxonomy

## 1. Amaç

Bu projede `memory` kelimesi her şeyi ifade etmemelidir. Aksi halde evidence atom, vector DB, candidate graph ve curated KG birbirine karışır.

Doğru ayrım:

```text
Evidence Archive      = her şeyi saklayan kanıt arşivi
Retrieval Substrate   = arşivi buldurmaya yarayan teknik indexler
Candidate Knowledge   = LLM/agent önerileri
Curated KG            = onaylı structured gerçeklik
Semantic Memory       = Curated KG'den üretilmiş öz bilgi
Working Memory        = LLM'in o anda gördüğü küçük context paketi
```

## 2. Evidence Archive

Memory değildir. Arşivdir.

Kapsar:

```text
raw files
parsed documents
evidence atoms
source metadata
source versions
ACL
parser outputs
OCR metadata
```

Kapsamaz:

```text
öz bilgi
güncel entity state
kullanıcıya doğrudan cevap
curated truth
```

## 3. Retrieval Substrate

Memory değildir. Arama altyapısıdır.

MVP'de:

```text
PostgreSQL text/metadata search
basic graph neighborhood query
```

Future'da:

```text
vector index
lexical search engine
entity mention index
reranking
evidence graph
```

Amaç agent veya ask sürecinde doğru context'i bulmaktır.

## 4. Candidate Knowledge Layer

Resmi gerçek değildir. Agentlerin öneri alanıdır.

Kapsar:

```text
candidate entity
candidate fact
candidate claim
candidate conflict
candidate graph patch
candidate ontology proposal
```

Kural:

```text
Candidate bilgi semantic memory'ye doğrudan giremez.
Candidate bilgi curated KG'ye doğrudan yazılamaz.
Candidate bilgi answer üretiminde ancak açıkça candidate olduğu belirtilerek kullanılabilir.
```

## 5. Curated Knowledge Graph

Onaylı structured gerçekliktir.

Kapsar:

```text
published nodes
published assertions
published relations
active/expired/retracted/superseded validity state
evidence refs
approval metadata
ontology version
```

Kapsamaz:

```text
raw documents
unvalidated LLM output
rejected candidates
unapproved graph patches
```

## 6. Semantic Memory

Asıl memory katmanıdır.

Tanım:

```text
Semantic Memory, Curated KG'den üretilmiş, kanıta bağlı,
güncel, öz, access-controlled, entity/process/event merkezli bilgi durumudur.
```

Semantic memory hem doğal dil özeti hem structured fact referansları taşır.

Kapsar:

```text
entity state
current facts
important historical facts
open conflicts
freshness
owner team
ACL
evidence references
curated assertion references
```

Kapsamaz:

```text
ham PDF içeriği
her evidence atom
her candidate relation
LLM summary as primary evidence
geçici chat mesajları
kaynağı olmayan iddialar
```

## 7. SemanticMemoryItem schema

MVP için önerilen contract:

```json
{
  "id": "mem_sales_department_roles",
  "memoryType": "organization_state",
  "subjectType": "Department",
  "subjectId": "department_sales",
  "subjectName": "Satış Departmanı",
  "summary": "Güncel bilgiye göre satış başkanı Mehmet Demir, satış başkan yardımcısı Ayşe Kaya'dır.",
  "currentFactRefs": ["assert_002", "assert_003"],
  "importantHistoryRefs": ["assert_001"],
  "openConflictRefs": [],
  "evidenceAtomIds": ["atom_org_jan_001", "atom_org_jun_001"],
  "freshnessStatus": "current",
  "lastVerifiedAt": "2026-06-30T10:00:00+03:00",
  "ownerTeam": "HR",
  "accessPolicy": "hr_internal",
  "memoryVersion": 3,
  "generatedFrom": "curated_kg",
  "ontologyVersion": "demo_ontology_v2"
}
```

## 8. Working Memory

Working Memory geçicidir. LLM veya agent'in o anki görevi için hazırlanır.

Örnek:

```json
{
  "task": "Detect role assignment changes.",
  "newEvidenceAtoms": ["atom_org_jun_001"],
  "semanticMemory": {
    "currentSalesPresident": "Ayşe Kaya"
  },
  "existingCuratedFacts": [
    {
      "assertionId": "assert_001",
      "fact": "Ayşe Kaya holds SalesPresident",
      "validityStatus": "active"
    }
  ],
  "ontologyRules": [
    "SalesPresident maxActiveHolders = 1",
    "Role changes require human review",
    "Old assertions are not deleted; expire or supersede them"
  ],
  "expectedOutput": "GraphPatchProposal"
}
```

## 9. Memory'ye giriş kriterleri

Bir bilgi semantic memory'ye girmek için şu sorulara olumlu cevap vermelidir:

```text
Tekrar kullanılacak mı?
İş açısından önemli mi?
Curated KG'de karşılığı var mı?
Evidence'a bağlanabiliyor mu?
Güncellik durumu belli mi?
Owner team belli mi?
ACL belli mi?
Yanlışsa zararı olur mu?
```

## 10. Ana kural

```text
Archive her şeyi saklar.
Memory önemli olanı bilir.
Curated KG doğru olanı yapılandırır.
Working Memory o an gerekeni taşır.
```

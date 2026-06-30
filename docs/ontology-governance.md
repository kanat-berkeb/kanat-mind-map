# Ontology Governance

## 1. Amaç

Ontology, sistemin hangi entity ve relation tiplerini kullanabileceğini belirleyen canlı ama kontrollü sözleşmedir.

Ontology serbestçe değişirse extraction, validation, graph ve memory kırılır. Bu yüzden ontology versioned ve human-in-the-loop yönetilmelidir.

## 2. Ontology neyi kapsar?

```text
entity types
relation types
domain/range kuralları
required fields
cardinality kuralları
source authority kuralları
approval policy
ACL/sensitivity policy
freshness policy
deprecated types
migration notes
```

## 3. MVP ontology kapsamı

MVP'de ontology yönetimi basit tutulur.

```text
packages/ontology/demo-ontology.yaml manuel düzenlenir.
Her extraction job ontologyVersion taşır.
Candidate facts ontology'ye göre validate edilir.
Ontology proposal UI yapılmaz.
Migration engine yapılmaz.
```

MVP'de olması gereken minimum entity tipleri:

```text
Customer
Person
Team
Region
Product
Project
Service
Risk
SalesTarget
Decision
Document
Role
RoleAssignment
Department
EvidenceAtom
Conflict
SemanticMemoryItem
```

Minimum relation tipleri:

```text
managedBy
locatedIn
interestedIn
hasTarget
hasRisk
memberOf
ownsService
partOf
dependsOn
decidedIn
affects
mentions
holdsRole
hasRoleAssignment
supportedBy
supersedes
retractedBy
summarizes
```

## 4. Versioning

Her ontology değişikliği yeni versiyon üretir.

```text
demo_ontology_v1
demo_ontology_v2
sales_ontology_v1
hr_ontology_v1
```

Her candidate, validation result, graph patch ve published assertion şu bilgiyi taşımalıdır:

```text
ontologyVersion
extractionPromptVersion
validationRuleVersion
```

## 5. Source authority kuralları

Her fact tipi için authoritative source tanımlanmalıdır.

Örnek:

```yaml
sourceAuthority:
  roleAssignment:
    primary:
      - HRSystem
      - ApprovedOrgChart
    secondary:
      - MeetingNotes
      - Email
    conflictPolicy: human_review_required

  customerRepresentative:
    primary:
      - CRM
    secondary:
      - SalesMeetingNotes
    conflictPolicy: authoritative_source_wins

  salesActual:
    primary:
      - ERP
    secondary: []
    conflictPolicy: authoritative_source_wins
```

## 6. Cardinality kuralları

Bazı relation'lar tekil olmalıdır.

Örnek:

```yaml
cardinalityRules:
  SalesPresident:
    maxActiveHolders: 1
    overlapAllowed: false
    changeRequiresHumanReview: true
```

Bu kural sayesinde sistem aynı anda iki aktif satış başkanı olmasını conflict olarak işaretler.

## 7. Ontology proposal akışı

Future aşamada agentler ontology'yi değiştirmez, sadece proposal üretir.

```text
Ontology gap detected
→ Ontology proposal
→ Impact analysis
→ Human ontology review
→ Approved/Rejected
→ New ontology version
→ Targeted re-extraction
```

Proposal tipleri:

```text
ADD_ENTITY_TYPE
ADD_RELATION_TYPE
ADD_REQUIRED_FIELD
CHANGE_CARDINALITY
DEPRECATE_TYPE
ADD_SOURCE_AUTHORITY_RULE
ADD_APPROVAL_RULE
ADD_ACL_RULE
```

## 8. Impact analysis

Ontology değişmeden önce şu sorular cevaplanmalıdır:

```text
Hangi extraction promptları değişecek?
Hangi validation kuralları değişecek?
Mevcut published assertion'lar etkilenecek mi?
Semantic memory kartları stale olacak mı?
Hangi evidence atomlar yeniden işlenmeli?
```

## 9. Targeted re-extraction

Ontology değişince tüm arşivi yeniden işlemek gerekmez. Sadece etkilenen domain ve evidence atomlar seçilir.

Örnek:

```text
CustomerSegment entity tipi eklendi.
Sadece müşteri dokümanları ve segment kelimeleri geçen atomlar yeniden işlenir.
```

## 10. Ana kural

```text
Agent ontology'yi değiştirmez.
Agent ontology proposal üretir.
İnsan/domain owner onaylar.
Yeni ontology version çıkar.
Eski graph ve memory kontrollü migrate edilir.
```

# Data Model Spec

## 1. Amaç

Bu dosya `kanat-mind-map` için hedef veri modellerini netleştirir. Amaç, mimarinin sadece kavramsal kalmaması ve NestJS/FastAPI/Prisma tarafında uygulanabilir hale gelmesidir.

MVP'de tüm modellerin eksiksiz kodlanması gerekmez. Ancak model sınırları baştan doğru çizilmelidir.

## 2. Naming convention

```text
External API contract: camelCase
NestJS DTO: camelCase
Prisma model fields: camelCase
FastAPI internal Python: snake_case olabilir
FastAPI response: camelCase alias ile dönmeli
Concept docs: snake_case kullanılabilir ama canonical contract camelCase'tir
```

## 3. Document

Kaynak dosya metadata kaydıdır.

```json
{
  "id": "doc_001",
  "fileName": "org_update_2026_jun.pdf",
  "fileType": "pdf",
  "sourceType": "pdf",
  "storagePath": "/uploads/org_update_2026_jun.pdf",
  "status": "uploaded",
  "accessPolicy": "hr_internal",
  "createdAt": "2026-06-30T10:00:00+03:00",
  "updatedAt": "2026-06-30T10:00:00+03:00"
}
```

## 4. EvidenceAtom

Kaynak kanıt parçasıdır. Memory değildir.

```json
{
  "id": "atom_001",
  "atomId": "org-update-2026:a001",
  "documentId": "doc_001",
  "sourceId": "src_001",
  "sourceVersion": "v1",
  "atomIndex": 1,
  "atomType": "paragraph",
  "sourceType": "pdf",
  "text": "Mehmet Demir satış başkanı, Ayşe Kaya satış başkan yardımcısıdır.",
  "structuredContent": null,
  "location": { "page": 1, "block": 2 },
  "sectionPath": ["Organizasyon", "Satış"],
  "qualityScore": 92,
  "contentHash": "sha256:...",
  "accessPolicy": "hr_internal",
  "metadata": {}
}
```

## 5. CandidateFact

LLM/agent tarafından çıkarılmış aday bilgidir. Resmi gerçek değildir.

```json
{
  "id": "cand_001",
  "subjectName": "Mehmet Demir",
  "subjectType": "Person",
  "predicate": "holdsRole",
  "objectName": "Satış Başkanı",
  "objectType": "Role",
  "objectProperties": {},
  "evidenceAtomIds": ["atom_001"],
  "sourceDocumentId": "doc_001",
  "evidenceText": "Mehmet Demir satış başkanı...",
  "llmConfidence": 0.91,
  "approvalScore": 91,
  "reviewStatus": "candidate",
  "publicationStatus": "unpublished",
  "validityStatus": "unknown",
  "validFrom": "2026-06-15",
  "validUntil": null,
  "ontologyVersion": "demo_ontology_v2"
}
```

## 6. ValidationResult

Candidate fact veya graph patch validation sonuçlarını tutar.

```json
{
  "id": "val_001",
  "targetType": "CandidateFact",
  "targetId": "cand_001",
  "overallStatus": "needs_review",
  "severity": "warning",
  "checks": [
    {
      "name": "ontology_validation",
      "status": "passed",
      "message": "Relation is allowed."
    },
    {
      "name": "cardinality_validation",
      "status": "failed",
      "message": "Another active SalesPresident exists."
    }
  ],
  "recommendedAction": "create_role_transition_patch",
  "createdAt": "2026-06-30T10:00:00+03:00"
}
```

## 7. ReviewDecision

İnsan review kararını tutar.

```json
{
  "id": "review_001",
  "targetType": "GraphPatch",
  "targetId": "patch_001",
  "decision": "approved",
  "reviewerId": "user_001",
  "reviewerTeam": "HR",
  "reason": "Approved organization update.",
  "createdAt": "2026-06-30T10:15:00+03:00"
}
```

## 8. ConflictRecord

Çelişkili bilgileri tutar.

```json
{
  "id": "conflict_001",
  "conflictType": "role_cardinality_conflict",
  "subjectId": "department_sales",
  "predicate": "hasSalesPresident",
  "candidateIds": ["cand_001"],
  "existingAssertionIds": ["assert_001"],
  "status": "needs_review",
  "resolution": null,
  "ownerTeam": "HR"
}
```

## 9. GraphPatch

Curated KG değişiklik paketidir.

```json
{
  "id": "patch_001",
  "patchType": "role_transition",
  "status": "needs_review",
  "operations": [
    {
      "op": "EXPIRE_ASSERTION",
      "assertionId": "assert_001",
      "validUntil": "2026-06-15"
    },
    {
      "op": "ADD_ASSERTION",
      "subjectId": "person_mehmet",
      "predicate": "holdsRole",
      "objectId": "role_sales_president",
      "validFrom": "2026-06-15"
    }
  ],
  "evidenceAtomIds": ["atom_001"],
  "validationResultIds": ["val_001"],
  "requiresHumanReview": true,
  "ontologyVersion": "demo_ontology_v2"
}
```

## 10. PublishedAssertion

Curated KG'deki onaylı assertion kaydıdır. PostgreSQL audit/source-of-truth olarak tutulur, Neo4j bunun projection'ıdır.

```json
{
  "id": "assert_002",
  "subjectId": "person_mehmet",
  "subjectType": "Person",
  "predicate": "holdsRole",
  "objectId": "role_sales_president",
  "objectType": "Role",
  "evidenceAtomIds": ["atom_001"],
  "reviewStatus": "approved",
  "publicationStatus": "published",
  "validityStatus": "active",
  "validFrom": "2026-06-15",
  "validUntil": null,
  "knownFrom": "2026-06-30T10:15:00+03:00",
  "supersedes": ["assert_001"],
  "accessPolicy": "hr_internal",
  "ontologyVersion": "demo_ontology_v2"
}
```

## 11. SemanticMemoryItem

Curated KG'den türetilmiş öz bilgi kartıdır.

```json
{
  "id": "mem_sales_roles",
  "memoryType": "organization_state",
  "subjectType": "Department",
  "subjectId": "department_sales",
  "subjectName": "Satış Departmanı",
  "summary": "Güncel bilgiye göre satış başkanı Mehmet Demir, satış başkan yardımcısı Ayşe Kaya'dır.",
  "currentFactRefs": ["assert_002", "assert_003"],
  "importantHistoryRefs": ["assert_001"],
  "openConflictRefs": [],
  "evidenceAtomIds": ["atom_001"],
  "freshnessStatus": "current",
  "ownerTeam": "HR",
  "accessPolicy": "hr_internal",
  "memoryVersion": 1,
  "generatedFrom": "curated_kg"
}
```

## 12. OntologyVersion

```json
{
  "id": "ont_v2",
  "name": "demo_ontology_v2",
  "status": "active",
  "filePath": "packages/ontology/demo-ontology.yaml",
  "checksum": "sha256:...",
  "createdAt": "2026-06-30T10:00:00+03:00"
}
```

## 13. OntologyProposal

```json
{
  "id": "ont_prop_001",
  "proposalType": "ADD_ENTITY_TYPE",
  "proposedChange": {
    "entityType": "CustomerSegment"
  },
  "reason": "Frequent mentions of bayi, distribütör and ana sanayi.",
  "evidenceAtomIds": ["atom_010", "atom_011"],
  "status": "needs_review",
  "ownerTeam": "Sales Operations"
}
```

## 14. MVP minimum modeller

MVP'de ilk etapta zorunlu modeller:

```text
Document
EvidenceAtom
CandidateFact
ValidationResult
GraphPatch
PublishedAssertion
SemanticMemoryItem
```

Sonraki etap modeller:

```text
ConflictRecord
ReviewDecision
OntologyVersion
OntologyProposal
```

Ancak bu sonraki modellerin field'ları şimdiden DTO/metadata içinde düşünülmelidir.

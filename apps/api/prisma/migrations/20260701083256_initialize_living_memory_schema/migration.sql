-- CreateEnum
CREATE TYPE "ReviewStatus" AS ENUM ('candidate', 'validated', 'needs_review', 'approved', 'rejected');

-- CreateEnum
CREATE TYPE "PublicationStatus" AS ENUM ('unpublished', 'publish_pending', 'published', 'publish_failed');

-- CreateEnum
CREATE TYPE "ValidityStatus" AS ENUM ('active', 'expired', 'superseded', 'retracted', 'conflicted');

-- CreateEnum
CREATE TYPE "ValidationStatus" AS ENUM ('passed', 'failed', 'warning', 'skipped', 'needs_review');

-- CreateEnum
CREATE TYPE "ValidationSeverity" AS ENUM ('info', 'warning', 'error', 'critical');

-- CreateEnum
CREATE TYPE "ReviewDecisionType" AS ENUM ('approved', 'rejected');

-- CreateEnum
CREATE TYPE "ConflictStatus" AS ENUM ('open', 'needs_review', 'resolved', 'dismissed');

-- CreateEnum
CREATE TYPE "FreshnessStatus" AS ENUM ('current', 'stale', 'needs_verification');

-- CreateEnum
CREATE TYPE "MemoryGenerationSource" AS ENUM ('curated_kg', 'published_assertions');

-- CreateEnum
CREATE TYPE "DocumentStatus" AS ENUM ('uploaded', 'extracting', 'extracted', 'failed');

-- CreateTable
CREATE TABLE "Document" (
    "id" TEXT NOT NULL,
    "fileName" TEXT NOT NULL,
    "fileType" TEXT NOT NULL,
    "sourceType" TEXT NOT NULL,
    "storagePath" TEXT NOT NULL,
    "status" "DocumentStatus" NOT NULL DEFAULT 'uploaded',
    "accessPolicy" TEXT NOT NULL,
    "extractionMetadata" JSONB,
    "extractionWarnings" JSONB,
    "extractionError" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Document_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "EvidenceAtom" (
    "id" TEXT NOT NULL,
    "atomId" TEXT NOT NULL,
    "documentId" TEXT NOT NULL,
    "sourceId" TEXT NOT NULL,
    "sourceVersion" TEXT NOT NULL,
    "atomIndex" INTEGER NOT NULL,
    "atomType" TEXT NOT NULL,
    "sourceType" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "structuredContent" JSONB,
    "location" JSONB,
    "sectionPath" TEXT[],
    "parentAtomId" TEXT,
    "qualityScore" INTEGER NOT NULL,
    "contentHash" TEXT NOT NULL,
    "accessPolicy" TEXT NOT NULL,
    "metadata" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "EvidenceAtom_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CandidateFact" (
    "id" TEXT NOT NULL,
    "subjectName" TEXT NOT NULL,
    "subjectType" TEXT NOT NULL,
    "predicate" TEXT NOT NULL,
    "objectName" TEXT NOT NULL,
    "objectType" TEXT NOT NULL,
    "objectProperties" JSONB,
    "evidenceAtomIds" TEXT[],
    "sourceDocumentId" TEXT,
    "evidenceText" TEXT NOT NULL,
    "llmConfidence" DOUBLE PRECISION,
    "approvalScore" INTEGER,
    "reviewStatus" "ReviewStatus" NOT NULL DEFAULT 'candidate',
    "publicationStatus" "PublicationStatus" NOT NULL DEFAULT 'unpublished',
    "validityStatus" "ValidityStatus",
    "ontologyVersion" TEXT,
    "validationSummary" JSONB,
    "accessPolicy" TEXT,
    "validFrom" TIMESTAMP(3),
    "validUntil" TIMESTAMP(3),
    "knownFrom" TIMESTAMP(3),
    "knownUntil" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "CandidateFact_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ValidationResult" (
    "id" TEXT NOT NULL,
    "candidateFactId" TEXT NOT NULL,
    "overallStatus" "ValidationStatus" NOT NULL,
    "severity" "ValidationSeverity" NOT NULL,
    "checks" JSONB NOT NULL,
    "recommendedAction" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ValidationResult_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ReviewDecision" (
    "id" TEXT NOT NULL,
    "candidateFactId" TEXT NOT NULL,
    "reviewerId" TEXT,
    "decision" "ReviewDecisionType" NOT NULL,
    "reason" TEXT,
    "changedFields" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ReviewDecision_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ConflictRecord" (
    "id" TEXT NOT NULL,
    "conflictType" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "subjectType" TEXT,
    "predicate" TEXT NOT NULL,
    "candidateIds" TEXT[],
    "existingAssertionIds" TEXT[],
    "status" "ConflictStatus" NOT NULL DEFAULT 'needs_review',
    "resolution" JSONB,
    "ownerTeam" TEXT,
    "accessPolicy" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "resolvedAt" TIMESTAMP(3),

    CONSTRAINT "ConflictRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GraphPatch" (
    "id" TEXT NOT NULL,
    "patchType" TEXT NOT NULL,
    "operations" JSONB NOT NULL,
    "evidenceAtomIds" TEXT[],
    "validationResultId" TEXT,
    "reviewStatus" "ReviewStatus" NOT NULL DEFAULT 'needs_review',
    "publicationStatus" "PublicationStatus" NOT NULL DEFAULT 'unpublished',
    "requiresHumanReview" BOOLEAN NOT NULL DEFAULT true,
    "ontologyVersion" TEXT NOT NULL,
    "accessPolicy" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "appliedAt" TIMESTAMP(3),

    CONSTRAINT "GraphPatch_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PublishedAssertion" (
    "id" TEXT NOT NULL,
    "subjectType" TEXT NOT NULL,
    "subjectName" TEXT NOT NULL,
    "predicate" TEXT NOT NULL,
    "objectType" TEXT NOT NULL,
    "objectName" TEXT NOT NULL,
    "objectProperties" JSONB,
    "evidenceAtomIds" JSONB NOT NULL,
    "sourceDocumentId" TEXT,
    "graphPatchId" TEXT,
    "reviewStatus" "ReviewStatus" NOT NULL DEFAULT 'approved',
    "publicationStatus" "PublicationStatus" NOT NULL DEFAULT 'published',
    "validityStatus" "ValidityStatus" NOT NULL,
    "validFrom" TIMESTAMP(3),
    "validUntil" TIMESTAMP(3),
    "knownFrom" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "knownUntil" TIMESTAMP(3),
    "supersedes" TEXT[],
    "retractedBy" TEXT,
    "accessPolicy" TEXT NOT NULL,
    "ontologyVersion" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PublishedAssertion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SemanticMemoryItem" (
    "id" TEXT NOT NULL,
    "memoryType" TEXT NOT NULL,
    "subjectType" TEXT NOT NULL,
    "subjectId" TEXT NOT NULL,
    "subjectName" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "currentFacts" JSONB NOT NULL,
    "importantHistory" JSONB,
    "openConflictRefs" JSONB,
    "evidenceRefs" JSONB NOT NULL,
    "accessPolicy" TEXT NOT NULL,
    "freshnessStatus" "FreshnessStatus" NOT NULL DEFAULT 'needs_verification',
    "lastVerifiedAt" TIMESTAMP(3),
    "ownerTeam" TEXT,
    "memoryVersion" INTEGER NOT NULL DEFAULT 1,
    "generatedFrom" "MemoryGenerationSource" NOT NULL DEFAULT 'curated_kg',
    "ontologyVersion" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "SemanticMemoryItem_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Document_status_createdAt_idx" ON "Document"("status", "createdAt");

-- CreateIndex
CREATE INDEX "EvidenceAtom_documentId_atomIndex_idx" ON "EvidenceAtom"("documentId", "atomIndex");

-- CreateIndex
CREATE UNIQUE INDEX "EvidenceAtom_documentId_atomId_key" ON "EvidenceAtom"("documentId", "atomId");

-- CreateIndex
CREATE INDEX "CandidateFact_sourceDocumentId_createdAt_idx" ON "CandidateFact"("sourceDocumentId", "createdAt");

-- CreateIndex
CREATE INDEX "ValidationResult_candidateFactId_createdAt_idx" ON "ValidationResult"("candidateFactId", "createdAt");

-- CreateIndex
CREATE INDEX "ReviewDecision_candidateFactId_createdAt_idx" ON "ReviewDecision"("candidateFactId", "createdAt");

-- CreateIndex
CREATE INDEX "ConflictRecord_status_createdAt_idx" ON "ConflictRecord"("status", "createdAt");

-- CreateIndex
CREATE INDEX "ConflictRecord_subjectId_predicate_idx" ON "ConflictRecord"("subjectId", "predicate");

-- CreateIndex
CREATE INDEX "GraphPatch_validationResultId_idx" ON "GraphPatch"("validationResultId");

-- CreateIndex
CREATE INDEX "GraphPatch_reviewStatus_publicationStatus_createdAt_idx" ON "GraphPatch"("reviewStatus", "publicationStatus", "createdAt");

-- CreateIndex
CREATE INDEX "PublishedAssertion_graphPatchId_idx" ON "PublishedAssertion"("graphPatchId");

-- CreateIndex
CREATE INDEX "PublishedAssertion_subjectType_subjectName_predicate_idx" ON "PublishedAssertion"("subjectType", "subjectName", "predicate");

-- CreateIndex
CREATE INDEX "PublishedAssertion_validityStatus_validFrom_validUntil_idx" ON "PublishedAssertion"("validityStatus", "validFrom", "validUntil");

-- CreateIndex
CREATE INDEX "SemanticMemoryItem_freshnessStatus_updatedAt_idx" ON "SemanticMemoryItem"("freshnessStatus", "updatedAt");

-- CreateIndex
CREATE INDEX "SemanticMemoryItem_subjectType_subjectName_idx" ON "SemanticMemoryItem"("subjectType", "subjectName");

-- CreateIndex
CREATE UNIQUE INDEX "SemanticMemoryItem_memoryType_subjectType_subjectId_key" ON "SemanticMemoryItem"("memoryType", "subjectType", "subjectId");

-- AddForeignKey
ALTER TABLE "EvidenceAtom" ADD CONSTRAINT "EvidenceAtom_documentId_fkey" FOREIGN KEY ("documentId") REFERENCES "Document"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CandidateFact" ADD CONSTRAINT "CandidateFact_sourceDocumentId_fkey" FOREIGN KEY ("sourceDocumentId") REFERENCES "Document"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ValidationResult" ADD CONSTRAINT "ValidationResult_candidateFactId_fkey" FOREIGN KEY ("candidateFactId") REFERENCES "CandidateFact"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReviewDecision" ADD CONSTRAINT "ReviewDecision_candidateFactId_fkey" FOREIGN KEY ("candidateFactId") REFERENCES "CandidateFact"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GraphPatch" ADD CONSTRAINT "GraphPatch_validationResultId_fkey" FOREIGN KEY ("validationResultId") REFERENCES "ValidationResult"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PublishedAssertion" ADD CONSTRAINT "PublishedAssertion_graphPatchId_fkey" FOREIGN KEY ("graphPatchId") REFERENCES "GraphPatch"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AlterTable
ALTER TABLE "ValidationResult" ADD COLUMN     "ontologyVersion" TEXT,
ADD COLUMN     "requiresHumanReview" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "validationRuleVersion" TEXT NOT NULL DEFAULT 'validation_rules_v1';

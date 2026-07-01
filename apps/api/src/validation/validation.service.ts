import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import type { Prisma } from '../generated/prisma/client';
import { PRISMA_SERVICE } from '../prisma/prisma.constants';
import type { PrismaService } from '../prisma/prisma.service';

const VALIDATION_RULE_VERSION = 'validation_rules_v1';

type CheckStatus = 'passed' | 'failed' | 'warning';
type CheckSeverity = 'info' | 'warning' | 'error';

export interface ValidationCheck {
  name: string;
  status: CheckStatus;
  severity: CheckSeverity;
  message: string;
  metadata?: Record<string, unknown>;
}

export interface CandidateValidationResult {
  id: string;
  targetType: 'CandidateFact';
  targetId: string;
  overallStatus: 'passed' | 'needs_review';
  severity: 'info' | 'error';
  checks: ValidationCheck[];
  recommendedAction: string;
  requiresHumanReview: boolean;
  ontologyVersion: string | null;
  validationRuleVersion: string;
  createdAt: Date;
}

@Injectable()
export class ValidationService {
  constructor(@Inject(PRISMA_SERVICE) private readonly prisma: PrismaService) {}

  async validateCandidateFact(
    candidateFactId: string,
  ): Promise<CandidateValidationResult> {
    const candidate = await this.prisma.candidateFact.findUnique({
      where: { id: candidateFactId },
      select: {
        id: true,
        subjectName: true,
        subjectType: true,
        predicate: true,
        objectName: true,
        objectType: true,
        evidenceAtomIds: true,
        sourceDocumentId: true,
        evidenceText: true,
        llmConfidence: true,
        validFrom: true,
        validUntil: true,
        ontologyVersion: true,
      },
    });
    if (!candidate) throw new NotFoundException('CandidateFact bulunamadı.');

    const evidenceIds = [...new Set(candidate.evidenceAtomIds)];
    const existingEvidence = candidate.sourceDocumentId
      ? await this.prisma.evidenceAtom.findMany({
          where: {
            documentId: candidate.sourceDocumentId,
            atomId: { in: evidenceIds },
          },
          select: { atomId: true },
        })
      : [];
    const checks = [
      this.schemaCheck(candidate),
      this.evidencePresenceCheck(evidenceIds, existingEvidence),
      this.confidenceCheck(candidate.llmConfidence),
      this.temporalCheck(candidate.validFrom, candidate.validUntil),
    ];
    const requiresHumanReview = checks.some(
      (check) => check.status === 'failed',
    );
    const overallStatus = requiresHumanReview ? 'needs_review' : 'passed';
    const severity = requiresHumanReview ? 'error' : 'info';
    const reviewStatus = requiresHumanReview ? 'needs_review' : 'validated';
    const recommendedAction = requiresHumanReview
      ? 'human_review_required'
      : 'continue_to_review_policy';

    const persisted = await this.prisma.$transaction(async (transaction) => {
      const validationResult = await transaction.validationResult.create({
        data: {
          candidateFactId,
          overallStatus,
          severity,
          checks: checks as unknown as Prisma.InputJsonValue,
          recommendedAction,
          requiresHumanReview,
          ontologyVersion: candidate.ontologyVersion,
          validationRuleVersion: VALIDATION_RULE_VERSION,
        },
      });
      await transaction.candidateFact.update({
        where: { id: candidateFactId },
        data: {
          reviewStatus,
          validationSummary: {
            validationResultId: validationResult.id,
            overallStatus,
            severity,
            requiresHumanReview,
          },
        },
      });
      return validationResult;
    });

    return {
      id: persisted.id,
      targetType: 'CandidateFact',
      targetId: candidateFactId,
      overallStatus,
      severity,
      checks,
      recommendedAction,
      requiresHumanReview,
      ontologyVersion: candidate.ontologyVersion,
      validationRuleVersion: VALIDATION_RULE_VERSION,
      createdAt: persisted.createdAt,
    };
  }

  private schemaCheck(candidate: {
    subjectName: string;
    subjectType: string;
    predicate: string;
    objectName: string;
    objectType: string;
    evidenceText: string;
  }): ValidationCheck {
    const values = [
      candidate.subjectName,
      candidate.subjectType,
      candidate.predicate,
      candidate.objectName,
      candidate.objectType,
      candidate.evidenceText,
    ];
    const passed = values.every((value) => value.trim().length > 0);
    return {
      name: 'schema_validation',
      status: passed ? 'passed' : 'failed',
      severity: passed ? 'info' : 'error',
      message: passed
        ? 'Candidate fact required fields are present.'
        : 'Candidate fact has empty required fields.',
    };
  }

  private evidencePresenceCheck(
    evidenceIds: string[],
    existingEvidence: { atomId: string }[],
  ): ValidationCheck {
    const existingIds = new Set(existingEvidence.map((item) => item.atomId));
    const missingIds = evidenceIds.filter((id) => !existingIds.has(id));
    const passed = evidenceIds.length > 0 && missingIds.length === 0;
    return {
      name: 'evidence_presence_validation',
      status: passed ? 'passed' : 'failed',
      severity: passed ? 'info' : 'error',
      message: passed
        ? 'All referenced evidence atoms exist.'
        : 'Referenced evidence atoms are empty or missing.',
      metadata: { missingEvidenceAtomIds: missingIds },
    };
  }

  private confidenceCheck(confidence: number | null): ValidationCheck {
    const passed = confidence !== null && confidence >= 0 && confidence <= 1;
    return {
      name: 'confidence_range_validation',
      status: passed ? 'passed' : 'failed',
      severity: passed ? 'info' : 'error',
      message: passed
        ? 'LLM confidence is within 0..1.'
        : 'LLM confidence must be within 0..1.',
    };
  }

  private temporalCheck(
    validFrom: Date | null,
    validUntil: Date | null,
  ): ValidationCheck {
    const passed = !validFrom || !validUntil || validUntil >= validFrom;
    return {
      name: 'temporal_basic_validation',
      status: passed ? 'passed' : 'failed',
      severity: passed ? 'info' : 'error',
      message: passed
        ? 'Candidate fact temporal range is valid.'
        : 'validUntil cannot be earlier than validFrom.',
    };
  }
}

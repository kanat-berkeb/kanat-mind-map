/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import type { PrismaService } from '../prisma/prisma.service';
import { ValidationService } from './validation.service';

describe('ValidationService', () => {
  const candidate = {
    id: 'fact-1',
    subjectName: 'ABC Boya',
    subjectType: 'Customer',
    predicate: 'hasTarget',
    objectName: '300 ton',
    objectType: 'SalesTarget',
    evidenceAtomIds: ['target:a001'],
    sourceDocumentId: 'doc-1',
    evidenceText: 'ABC Boya hedefi 300 tondur.',
    llmConfidence: 0.9,
    validFrom: new Date('2026-01-01'),
    validUntil: new Date('2026-12-31'),
    ontologyVersion: 'demo_ontology_v2',
  };

  function createPrisma(candidateValue: typeof candidate) {
    const validationCreate = jest.fn().mockResolvedValue({
      id: 'validation-1',
      createdAt: new Date('2026-07-01T10:00:00Z'),
    });
    const candidateUpdate = jest.fn().mockResolvedValue({});
    const transaction = {
      validationResult: { create: validationCreate },
      candidateFact: { update: candidateUpdate },
    };
    const prisma = {
      candidateFact: {
        findUnique: jest.fn().mockResolvedValue(candidateValue),
      },
      evidenceAtom: {
        findMany: jest
          .fn()
          .mockResolvedValue(
            candidateValue.evidenceAtomIds.map((atomId) => ({ atomId })),
          ),
      },
      $transaction: jest
        .fn()
        .mockImplementation((callback: (tx: typeof transaction) => unknown) =>
          Promise.resolve(callback(transaction)),
        ),
    } as unknown as PrismaService;
    return { prisma, validationCreate, candidateUpdate };
  }

  it('persists passed checks and marks candidate validated', async () => {
    const { prisma, validationCreate, candidateUpdate } =
      createPrisma(candidate);

    const result = await new ValidationService(prisma).validateCandidateFact(
      'fact-1',
    );

    expect(result.overallStatus).toBe('passed');
    expect(result.requiresHumanReview).toBe(false);
    expect(result.checks).toHaveLength(4);
    expect(result.checks.every((check) => check.status === 'passed')).toBe(
      true,
    );
    expect(validationCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          candidateFactId: 'fact-1',
          overallStatus: 'passed',
          requiresHumanReview: false,
        }),
      }),
    );
    expect(candidateUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({ reviewStatus: 'validated' }),
      }),
    );
  });

  it('marks invalid temporal and confidence checks for review', async () => {
    const invalidCandidate = {
      ...candidate,
      llmConfidence: 1.5,
      validFrom: new Date('2026-12-31'),
      validUntil: new Date('2026-01-01'),
    };
    const { prisma, candidateUpdate } = createPrisma(invalidCandidate);

    const result = await new ValidationService(prisma).validateCandidateFact(
      'fact-1',
    );

    expect(result.overallStatus).toBe('needs_review');
    expect(result.requiresHumanReview).toBe(true);
    expect(
      result.checks.filter((check) => check.status === 'failed'),
    ).toHaveLength(2);
    expect(candidateUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({ reviewStatus: 'needs_review' }),
      }),
    );
  });
});

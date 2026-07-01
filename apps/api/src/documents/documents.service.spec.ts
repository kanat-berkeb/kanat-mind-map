/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { writeFile, unlink } from 'node:fs/promises';
import { DocumentsService } from './documents.service';
import type { PrismaService } from '../prisma/prisma.service';

describe('DocumentsService', () => {
  const storagePath = '/tmp/kanat-document-extract-test.txt';

  afterEach(async () => {
    jest.restoreAllMocks();
    await unlink(storagePath).catch(() => undefined);
  });

  it('persists evidence and candidates with initial lifecycle states', async () => {
    await writeFile(storagePath, 'ABC Boya hedefi 300 tondur.');
    const evidenceCreate = jest.fn().mockResolvedValue({});
    const candidateCreate = jest.fn().mockResolvedValue({});
    const transactionDocumentUpdate = jest.fn().mockResolvedValue({});
    const documentUpdate = jest.fn().mockResolvedValue({});
    const transaction = {
      evidenceAtom: { create: evidenceCreate },
      candidateFact: { create: candidateCreate },
      document: { update: transactionDocumentUpdate },
    };
    const prisma = {
      document: {
        findUnique: jest.fn().mockResolvedValue({
          id: 'doc-1',
          fileName: 'target.txt',
          sourceType: 'txt',
          storagePath,
          status: 'uploaded',
        }),
        update: documentUpdate,
      },
      $transaction: jest
        .fn()
        .mockImplementation((callback: (tx: typeof transaction) => unknown) =>
          Promise.resolve(callback(transaction)),
        ),
    } as unknown as PrismaService;
    const payload = {
      evidenceAtoms: [
        {
          atomId: 'target:a001',
          documentId: 'upload:target',
          sourceId: 'target',
          sourceVersion: 'sha256:' + 'a'.repeat(64),
          atomIndex: 0,
          atomType: 'paragraph',
          sourceType: 'txt',
          text: 'ABC Boya hedefi 300 tondur.',
          structuredContent: null,
          location: null,
          sectionPath: [],
          parentAtomId: null,
          qualityScore: 90,
          contentHash: 'sha256:' + 'b'.repeat(64),
          accessPolicy: 'internal',
          metadata: {},
        },
      ],
      candidateFacts: [
        {
          subjectName: 'ABC Boya',
          subjectType: 'Customer',
          predicate: 'hasTarget',
          objectName: '300 ton',
          objectType: 'SalesTarget',
          objectProperties: { amount: 300, unit: 'ton' },
          evidenceAtomIds: ['target:a001'],
          evidenceText: 'ABC Boya hedefi 300 tondur.',
          llmConfidence: 0.9,
          approvalScore: 90,
          validFrom: null,
          validUntil: null,
          ontologyVersion: 'demo_ontology_v2',
          extractionWarnings: [],
        },
      ],
      metadata: { ontologyVersion: 'demo_ontology_v2' },
      warnings: [],
    };
    jest.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const result = await new DocumentsService(prisma).extract('doc-1');

    expect(result).toEqual(payload);
    expect(evidenceCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({ documentId: 'doc-1' }),
      }),
    );
    expect(candidateCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          sourceDocumentId: 'doc-1',
          reviewStatus: 'candidate',
          publicationStatus: 'unpublished',
          validityStatus: 'active',
          accessPolicy: 'internal',
        }),
      }),
    );
    expect(transactionDocumentUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({ status: 'extracted' }),
      }),
    );
  });

  it('returns document facts and evidence in stable order', async () => {
    const fact = {
      id: 'fact-1',
      reviewStatus: 'candidate',
      publicationStatus: 'unpublished',
      validityStatus: 'active',
      evidenceAtomIds: ['target:a001'],
      evidenceText: 'ABC Boya hedefi 300 tondur.',
      validationSummary: null,
    };
    const atom = {
      id: 'atom-1',
      atomId: 'target:a001',
      atomIndex: 0,
      text: 'ABC Boya hedefi 300 tondur.',
    };
    const findFacts = jest.fn().mockResolvedValue([fact]);
    const findAtoms = jest.fn().mockResolvedValue([atom]);
    const prisma = {
      document: { findUnique: jest.fn().mockResolvedValue({ id: 'doc-1' }) },
      candidateFact: { findMany: findFacts },
      evidenceAtom: { findMany: findAtoms },
    } as unknown as PrismaService;
    const service = new DocumentsService(prisma);

    await expect(service.getFacts('doc-1')).resolves.toEqual([fact]);
    await expect(service.getEvidenceAtoms('doc-1')).resolves.toEqual([atom]);
    expect(findFacts).toHaveBeenCalledWith(
      expect.objectContaining({
        where: { sourceDocumentId: 'doc-1' },
        orderBy: { createdAt: 'asc' },
        select: expect.objectContaining({
          reviewStatus: true,
          publicationStatus: true,
          validityStatus: true,
          validationSummary: true,
          evidenceAtomIds: true,
          evidenceText: true,
        }),
      }),
    );
    expect(findAtoms).toHaveBeenCalledWith(
      expect.objectContaining({
        where: { documentId: 'doc-1' },
        orderBy: { atomIndex: 'asc' },
      }),
    );
  });
});

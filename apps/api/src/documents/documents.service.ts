import {
  BadGatewayException,
  BadRequestException,
  ConflictException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { readFile } from 'node:fs/promises';
import { extname } from 'node:path';
import type { Prisma } from '../generated/prisma/client';
import type { PrismaService } from '../prisma/prisma.service';

const ALLOWED_EXTENSIONS = new Set(['.pdf', '.txt', '.md']);
const ALLOWED_SOURCE_TYPES = new Set([
  'pdf',
  'txt',
  'transcript',
  'markdown',
  'software_note',
]);

export interface UploadedDocument {
  originalname: string;
  mimetype: string;
  size: number;
  buffer: Buffer;
}

interface EvidenceLocation {
  page: number | null;
  block: number | null;
  lineStart: number | null;
  lineEnd: number | null;
  charStart: number | null;
  charEnd: number | null;
}

interface EvidenceAtomResponse {
  atomId: string;
  documentId: string;
  sourceId: string;
  sourceVersion: string;
  atomIndex: number;
  atomType: string;
  sourceType: string;
  text: string;
  structuredContent: unknown;
  location: EvidenceLocation | null;
  sectionPath: string[];
  parentAtomId: string | null;
  qualityScore: number;
  contentHash: string;
  accessPolicy: string;
  metadata: Record<string, unknown>;
}

interface CandidateFactResponse {
  subjectName: string;
  subjectType: string;
  predicate: string;
  objectName: string;
  objectType: string;
  objectProperties: Record<string, unknown> | null;
  evidenceAtomIds: string[];
  evidenceText: string;
  llmConfidence: number;
  approvalScore: number;
  validFrom: string | null;
  validUntil: string | null;
  ontologyVersion: string;
  extractionWarnings: string[];
}

interface ProcessDocumentResponse {
  evidenceAtoms: EvidenceAtomResponse[];
  candidateFacts: CandidateFactResponse[];
  metadata: Record<string, unknown>;
  warnings: Record<string, unknown>[];
}

@Injectable()
export class DocumentsService {
  constructor(private readonly prisma: PrismaService) {}

  async getDocument(documentId: string): Promise<unknown> {
    const document = await this.prisma.document.findUnique({
      where: { id: documentId },
      select: {
        id: true,
        fileName: true,
        fileType: true,
        sourceType: true,
        status: true,
        accessPolicy: true,
        extractionMetadata: true,
        extractionWarnings: true,
        extractionError: true,
        createdAt: true,
        updatedAt: true,
      },
    });
    if (!document) throw new NotFoundException('Document bulunamadı.');
    return document;
  }

  async getFacts(documentId: string): Promise<unknown> {
    await this.requireDocument(documentId);
    return this.prisma.candidateFact.findMany({
      where: { sourceDocumentId: documentId },
      orderBy: { createdAt: 'asc' },
      select: {
        id: true,
        subjectName: true,
        subjectType: true,
        predicate: true,
        objectName: true,
        objectType: true,
        objectProperties: true,
        evidenceAtomIds: true,
        sourceDocumentId: true,
        evidenceText: true,
        llmConfidence: true,
        approvalScore: true,
        reviewStatus: true,
        publicationStatus: true,
        validityStatus: true,
        ontologyVersion: true,
        validationSummary: true,
        accessPolicy: true,
        validFrom: true,
        validUntil: true,
        knownFrom: true,
        knownUntil: true,
        createdAt: true,
        updatedAt: true,
      },
    });
  }

  async getEvidenceAtoms(documentId: string): Promise<unknown> {
    await this.requireDocument(documentId);
    return this.prisma.evidenceAtom.findMany({
      where: { documentId },
      orderBy: { atomIndex: 'asc' },
      select: {
        id: true,
        atomId: true,
        documentId: true,
        sourceId: true,
        sourceVersion: true,
        atomIndex: true,
        atomType: true,
        sourceType: true,
        text: true,
        structuredContent: true,
        location: true,
        sectionPath: true,
        parentAtomId: true,
        qualityScore: true,
        contentHash: true,
        accessPolicy: true,
        metadata: true,
        createdAt: true,
      },
    });
  }

  async process(
    file: UploadedDocument,
    sourceType: string | undefined,
  ): Promise<ProcessDocumentResponse> {
    this.validateFile(file, sourceType);
    return this.callAi(file, sourceType as string);
  }

  async extract(documentId: string): Promise<ProcessDocumentResponse> {
    const document = await this.prisma.document.findUnique({
      where: { id: documentId },
    });
    if (!document) throw new NotFoundException('Document bulunamadı.');
    if (document.status === 'extracted' || document.status === 'extracting') {
      throw new ConflictException('Document extraction daha önce başlatılmış.');
    }

    let buffer: Buffer;
    try {
      buffer = await readFile(document.storagePath);
    } catch {
      await this.markFailed(documentId, 'Source dosyası okunamadı.');
      throw new BadRequestException('Document source dosyası okunamadı.');
    }

    const file: UploadedDocument = {
      originalname: document.fileName,
      mimetype: this.mimeType(document.fileName),
      size: buffer.length,
      buffer,
    };
    this.validateFile(file, document.sourceType);
    await this.prisma.document.update({
      where: { id: documentId },
      data: { status: 'extracting', extractionError: null },
    });

    let payload: ProcessDocumentResponse;
    try {
      payload = await this.callAi(file, document.sourceType);
      await this.persistExtraction(documentId, payload);
    } catch (error) {
      await this.markFailed(documentId, this.errorMessage(error));
      throw error;
    }
    return payload;
  }

  private async persistExtraction(
    documentId: string,
    payload: ProcessDocumentResponse,
  ): Promise<void> {
    await this.prisma.$transaction(async (transaction) => {
      for (const atom of payload.evidenceAtoms) {
        await transaction.evidenceAtom.create({
          data: {
            atomId: atom.atomId,
            documentId,
            sourceId: atom.sourceId,
            sourceVersion: atom.sourceVersion,
            atomIndex: atom.atomIndex,
            atomType: atom.atomType,
            sourceType: atom.sourceType,
            text: atom.text,
            structuredContent: this.optionalJson(atom.structuredContent),
            location: this.optionalJson(atom.location),
            sectionPath: atom.sectionPath,
            parentAtomId: atom.parentAtomId,
            qualityScore: atom.qualityScore,
            contentHash: atom.contentHash,
            accessPolicy: atom.accessPolicy,
            metadata: atom.metadata as Prisma.InputJsonValue,
          },
        });
      }
      for (const fact of payload.candidateFacts) {
        await transaction.candidateFact.create({
          data: {
            subjectName: fact.subjectName,
            subjectType: fact.subjectType,
            predicate: fact.predicate,
            objectName: fact.objectName,
            objectType: fact.objectType,
            objectProperties: this.optionalJson(fact.objectProperties),
            evidenceAtomIds: fact.evidenceAtomIds,
            sourceDocumentId: documentId,
            evidenceText: fact.evidenceText,
            llmConfidence: fact.llmConfidence,
            approvalScore: fact.approvalScore,
            reviewStatus: 'candidate',
            publicationStatus: 'unpublished',
            validityStatus: 'active',
            ontologyVersion: fact.ontologyVersion,
            accessPolicy: this.narrowAccessPolicy(
              fact.evidenceAtomIds,
              payload.evidenceAtoms,
            ),
            validFrom: fact.validFrom ? new Date(fact.validFrom) : null,
            validUntil: fact.validUntil ? new Date(fact.validUntil) : null,
            knownFrom: new Date(),
          },
        });
      }
      await transaction.document.update({
        where: { id: documentId },
        data: {
          status: 'extracted',
          extractionMetadata: payload.metadata as Prisma.InputJsonValue,
          extractionWarnings: payload.warnings as Prisma.InputJsonValue,
          extractionError: null,
        },
      });
    });
  }

  private async requireDocument(documentId: string): Promise<void> {
    const document = await this.prisma.document.findUnique({
      where: { id: documentId },
      select: { id: true },
    });
    if (!document) throw new NotFoundException('Document bulunamadı.');
  }

  private narrowAccessPolicy(
    evidenceAtomIds: string[],
    atoms: EvidenceAtomResponse[],
  ): string {
    const policies = new Set(
      atoms
        .filter((atom) => evidenceAtomIds.includes(atom.atomId))
        .map((atom) => atom.accessPolicy),
    );
    if (policies.size !== 1) {
      throw new BadGatewayException(
        'Candidate fact evidence accessPolicy değerleri uyumsuz.',
      );
    }
    return [...policies][0];
  }

  private optionalJson(value: unknown): Prisma.InputJsonValue | undefined {
    return value === null || value === undefined ? undefined : value;
  }

  private async markFailed(documentId: string, message: string): Promise<void> {
    await this.prisma.document.update({
      where: { id: documentId },
      data: { status: 'failed', extractionError: message.slice(0, 1000) },
    });
  }

  private validateFile(
    file: UploadedDocument,
    sourceType: string | undefined,
  ): void {
    if (!ALLOWED_EXTENSIONS.has(extname(file.originalname).toLowerCase())) {
      throw new BadRequestException('Yalnız PDF, TXT ve MD kabul edilir.');
    }
    if (!sourceType || !ALLOWED_SOURCE_TYPES.has(sourceType)) {
      throw new BadRequestException('Geçersiz sourceType.');
    }
  }

  private mimeType(fileName: string): string {
    const extension = extname(fileName).toLowerCase();
    if (extension === '.pdf') return 'application/pdf';
    if (extension === '.md') return 'text/markdown';
    return 'text/plain';
  }

  private async callAi(
    file: UploadedDocument,
    sourceType: string,
  ): Promise<ProcessDocumentResponse> {
    const form = new FormData();
    form.append(
      'file',
      new Blob([new Uint8Array(file.buffer)], { type: file.mimetype }),
      file.originalname,
    );
    form.append('sourceType', sourceType);

    let response: Response;
    try {
      response = await fetch(
        `${process.env.AI_API_BASE_URL ?? 'http://localhost:8000'}/process-document`,
        { method: 'POST', body: form },
      );
    } catch {
      throw new BadGatewayException('FastAPI servisine ulaşılamadı.');
    }
    const payload = await this.readJson(response);
    if (!response.ok) {
      throw new BadGatewayException({
        message: 'FastAPI dokümanı işleyemedi.',
        upstreamStatus: response.status,
        upstreamResponse: payload,
      });
    }
    if (!this.isProcessDocumentResponse(payload)) {
      throw new BadGatewayException('FastAPI response contract geçersiz.');
    }
    return payload;
  }

  private async readJson(response: Response): Promise<unknown> {
    const text = await response.text();
    try {
      return JSON.parse(text) as unknown;
    } catch {
      return text;
    }
  }

  private isProcessDocumentResponse(
    value: unknown,
  ): value is ProcessDocumentResponse {
    if (!this.isRecord(value)) return false;
    return (
      Array.isArray(value.evidenceAtoms) &&
      value.evidenceAtoms.every((atom) => this.isEvidenceAtom(atom)) &&
      Array.isArray(value.candidateFacts) &&
      value.candidateFacts.every((fact) => this.isCandidateFact(fact)) &&
      this.isRecord(value.metadata) &&
      Array.isArray(value.warnings) &&
      value.warnings.every((warning) => this.isRecord(warning))
    );
  }

  private isEvidenceAtom(value: unknown): value is EvidenceAtomResponse {
    if (!this.isRecord(value)) return false;
    return (
      this.isString(value.atomId) &&
      this.isString(value.documentId) &&
      this.isString(value.sourceId) &&
      this.isString(value.sourceVersion) &&
      Number.isInteger(value.atomIndex) &&
      this.isString(value.atomType) &&
      this.isString(value.sourceType) &&
      this.isString(value.text) &&
      value.text.length <= 1500 &&
      Array.isArray(value.sectionPath) &&
      value.sectionPath.every((item) => this.isString(item)) &&
      Number.isInteger(value.qualityScore) &&
      this.isString(value.contentHash) &&
      this.isString(value.accessPolicy) &&
      this.isRecord(value.metadata)
    );
  }

  private isCandidateFact(value: unknown): value is CandidateFactResponse {
    if (!this.isRecord(value)) return false;
    return (
      this.isString(value.subjectName) &&
      this.isString(value.subjectType) &&
      this.isString(value.predicate) &&
      this.isString(value.objectName) &&
      this.isString(value.objectType) &&
      Array.isArray(value.evidenceAtomIds) &&
      value.evidenceAtomIds.length > 0 &&
      value.evidenceAtomIds.every((item) => this.isString(item)) &&
      this.isString(value.evidenceText) &&
      typeof value.llmConfidence === 'number' &&
      value.llmConfidence >= 0 &&
      value.llmConfidence <= 1 &&
      Number.isInteger(value.approvalScore) &&
      this.isString(value.ontologyVersion) &&
      Array.isArray(value.extractionWarnings)
    );
  }

  private isRecord(value: unknown): value is Record<string, unknown> {
    return !!value && typeof value === 'object' && !Array.isArray(value);
  }

  private isString(value: unknown): value is string {
    return typeof value === 'string' && value.length > 0;
  }

  private errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : 'Extraction başarısız.';
  }
}

import {
  BadGatewayException,
  BadRequestException,
  Injectable,
} from '@nestjs/common';
import { extname } from 'node:path';

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

interface ProcessDocumentResponse {
  evidenceAtoms: unknown[];
  candidateFacts: unknown[];
  metadata: Record<string, unknown>;
  warnings: unknown[];
}

@Injectable()
export class DocumentsService {
  async process(
    file: UploadedDocument,
    sourceType: string | undefined,
  ): Promise<ProcessDocumentResponse> {
    if (!ALLOWED_EXTENSIONS.has(extname(file.originalname).toLowerCase())) {
      throw new BadRequestException('Yalnız PDF, TXT ve MD kabul edilir.');
    }
    if (!sourceType || !ALLOWED_SOURCE_TYPES.has(sourceType)) {
      throw new BadRequestException('Geçersiz sourceType.');
    }

    const form = new FormData();
    const bytes = new Uint8Array(file.buffer);
    form.append(
      'file',
      new Blob([bytes], { type: file.mimetype }),
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
    if (!value || typeof value !== 'object') return false;
    const record = value as Record<string, unknown>;
    return (
      Array.isArray(record.evidenceAtoms) &&
      Array.isArray(record.candidateFacts) &&
      !!record.metadata &&
      typeof record.metadata === 'object' &&
      Array.isArray(record.warnings)
    );
  }
}

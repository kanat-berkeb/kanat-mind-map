import {
  BadRequestException,
  Body,
  Controller,
  Get,
  Param,
  Post,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { DocumentsService, UploadedDocument } from './documents.service';

@Controller('documents')
export class DocumentsController {
  constructor(private readonly documentsService: DocumentsService) {}

  @Post('process')
  @UseInterceptors(
    FileInterceptor('file', {
      limits: { fileSize: 10 * 1024 * 1024, files: 1 },
    }),
  )
  processDocument(
    @UploadedFile() file: UploadedDocument | undefined,
    @Body('sourceType') sourceType: string | undefined,
  ): Promise<unknown> {
    if (!file) {
      throw new BadRequestException('file alanı zorunlu.');
    }
    return this.documentsService.process(file, sourceType);
  }

  @Post(':id/extract')
  extractDocument(@Param('id') id: string): Promise<unknown> {
    return this.documentsService.extract(id);
  }

  @Get(':id')
  getDocument(@Param('id') id: string): Promise<unknown> {
    return this.documentsService.getDocument(id);
  }

  @Get(':id/facts')
  getDocumentFacts(@Param('id') id: string): Promise<unknown> {
    return this.documentsService.getFacts(id);
  }

  @Get(':id/evidence-atoms')
  getDocumentEvidenceAtoms(@Param('id') id: string): Promise<unknown> {
    return this.documentsService.getEvidenceAtoms(id);
  }
}

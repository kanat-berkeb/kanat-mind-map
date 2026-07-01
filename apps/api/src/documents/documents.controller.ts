import {
  BadRequestException,
  Body,
  Controller,
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
}

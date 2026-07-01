import { Controller, Param, Post } from '@nestjs/common';
import { ValidationService } from './validation.service';

@Controller('candidate-facts')
export class ValidationController {
  constructor(private readonly validationService: ValidationService) {}

  @Post(':id/validate')
  validateCandidateFact(@Param('id') id: string): Promise<unknown> {
    return this.validationService.validateCandidateFact(id);
  }
}

import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';
import { PRISMA_SERVICE } from './prisma.constants';

@Global()
@Module({
  providers: [
    PrismaService,
    { provide: PRISMA_SERVICE, useExisting: PrismaService },
  ],
  exports: [PRISMA_SERVICE],
})
export class PrismaModule {}

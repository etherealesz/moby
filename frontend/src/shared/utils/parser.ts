import { z } from 'zod';
import { ParsingDataError } from '@/src/shared/errors';

export function safeParseZodObject<T>(
  schema: z.ZodType<T>,
  input: T,
  metadata?: Record<string, any>
) {
  const result = schema.safeParse(input);
  if (!result.success) {
    throw new ParsingDataError();
  }

  return result.data;
}

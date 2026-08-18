import { z } from 'zod';
import { SPagination } from './pagination';

export function StandardResponse<T>(data: z.ZodType<T>) {
  return z.object({
    meta: SMetaResponse,
    data,
    error: SStandardErrorResponse,
  });
}

export function StandardListResponse<T>(data: z.ZodArray<z.ZodType<T>>) {
  return z.object({
    meta: SMetaResponse,
    data,
    error: SStandardErrorResponse,
  });
}

const SMetaResponse = z
  .object({
    request_id: z.string(),
    timestamp: z.string(),
  })
  .extend(SPagination.shape);

const SStandardErrorResponse = z.object({
  status: z.boolean(),
  message: z.string(),
  detail: z.record(z.string(), z.string()).optional(),
  code: z.number(),
});

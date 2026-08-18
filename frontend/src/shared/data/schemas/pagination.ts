import { z } from 'zod';

export const SPagination = z.object({
  total: z.int().optional(),
  pages: z.int().optional(),
  per_page_size: z.int().optional(),
});

import z from 'zod';

function GridResponseData<T extends z.ZodType>(gridSchema: T) {
  return z.object({
    grid: gridSchema,
    grid_total: z.number(),
  });
}

function GridStandardResponse<T extends z.ZodType>(dataSchema: T) {
  return z.object({
    data: dataSchema,
  });
}

export const SStandardResponseGrid = GridStandardResponse(
  GridResponseData(z.array(z.any()))
);
export type TStandardResponseGrid = z.infer<typeof SStandardResponseGrid>;

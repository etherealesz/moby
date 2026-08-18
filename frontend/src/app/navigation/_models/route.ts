import { z } from 'zod';

/**
 * Zod Schema for Navigation Route Request
 */
export const RouteRequestSchema = z.object({
  start_lat: z
    .number()
    .min(-90)
    .max(90, 'Latitude awal harus antara -90 dan 90'),
  start_lon: z
    .number()
    .min(-180)
    .max(180, 'Longitude awal harus antara -180 dan 180'),
  end_lat: z
    .number()
    .min(-90)
    .max(90, 'Latitude tujuan harus antara -90 dan 90'),
  end_lon: z
    .number()
    .min(-180)
    .max(180, 'Longitude tujuan harus antara -180 dan 180'),
  mode: z.enum(['walk', 'drive']).default('walk'),
});

export type IRouteRequest = z.infer<typeof RouteRequestSchema>;

/**
 * Zod Schema for Single Coordinate Pair [lat, lon]
 */
export const CoordinatePairSchema = z.tuple([z.number(), z.number()]);
export type ICoordinatePair = z.infer<typeof CoordinatePairSchema>;

/**
 * Zod Schema for Navigation Route Response Payload
 */
export const RouteResponseDataSchema = z.object({
  distance_meters: z.number().nonnegative(),
  mode: z.string(),
  route: z.array(CoordinatePairSchema),
});

export type IRouteResponseData = z.infer<typeof RouteResponseDataSchema>;

/**
 * Standard API Response Wrapper Schema
 */
export const StandardRouteResponseSchema = z.object({
  status: z.number().optional(),
  message: z.string().optional(),
  data: RouteResponseDataSchema,
});

export type IStandardRouteResponse = z.infer<
  typeof StandardRouteResponseSchema
>;

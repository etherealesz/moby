import { defaultHttpClient } from '@/lib/api/http/client';
import {
  IRouteRequest,
  IRouteResponseData,
  RouteRequestSchema,
  StandardRouteResponseSchema,
} from '../_models/route';

/**
 * Service to request shortest path navigation route from backend
 */
export async function getRoute(
  payload: IRouteRequest
): Promise<IRouteResponseData> {
  // Validate request parameters using Zod
  const validatedPayload = RouteRequestSchema.parse(payload);

  const baseUrl =
    process.env.NEXT_PUBLIC_TRASH_NAV_API_BASE_URL || 'http://localhost:8000';

  // Try standard backend route path (supporting app prefix if configured)
  const endpoint = baseUrl.endsWith('/trashnav-development')
    ? `${baseUrl}/api/navigation/route`
    : `${baseUrl}/trashnav-development/api/navigation/route`;

  try {
    const response = await defaultHttpClient.post(endpoint, validatedPayload);
    const parsedResponse = StandardRouteResponseSchema.safeParse(response.data);

    if (parsedResponse.success) {
      return parsedResponse.data.data;
    }

    // Direct fallback if response is unnested
    if (response.data?.data) {
      return response.data.data as IRouteResponseData;
    }

    throw new Error('Format respon API rute tidak valid.');
  } catch (error: any) {
    // If prefix 404 occurs, attempt direct fallback to /api/navigation/route
    if (
      error?.response?.status === 404 &&
      endpoint.includes('/trashnav-development')
    ) {
      const fallbackEndpoint = `${baseUrl}/api/navigation/route`;
      const fallbackRes = await defaultHttpClient.post(
        fallbackEndpoint,
        validatedPayload
      );
      if (fallbackRes.data?.data) {
        return fallbackRes.data.data as IRouteResponseData;
      }
    }
    throw error;
  }
}

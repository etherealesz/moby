import { AxiosInstance } from 'axios';
import {
  httpClient as defaultHttpClient,
  generateCustomHttpClient,
} from './factory';

export { defaultHttpClient };

/**
 * Pre-configured HTTP clients for application services.
 */
const httpClient: Record<string, AxiosInstance> = {
  trashNav: generateCustomHttpClient({
    baseURL:
      process.env.NEXT_PUBLIC_TRASH_NAV_API_BASE_URL || 'http://localhost:8000',
  }),
} as const;

export default httpClient;

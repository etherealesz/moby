import { InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import {
  ACCESS_TOKEN_KEY,
  CSRF_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
} from '@/src/shared/constants/cookie';

/**
 * Interceptor related to authentication for HTTP requests.
 *
 * @param config - The Axios request configuration.
 *
 * @returns The modified Axios request configuration with authentication
 * if needed.
 */
export function onFullFilledAuthRequestInterceptor(
  config: InternalAxiosRequestConfig<any>
) {
  if (!config.headers.hasAuthorization() && !config.auth) {
    const [refreshToken, accessToken, csrfToken] = [
      Cookies.get(REFRESH_TOKEN_KEY),
      Cookies.get(ACCESS_TOKEN_KEY),
      Cookies.get(CSRF_TOKEN_KEY),
    ];

    // Change this after implementing a REAL backend authentication flow.
    if (refreshToken) {
      config.headers.setAuthorization(refreshToken);
    }

    if (csrfToken) {
      config.headers['x-csrftoken'] = csrfToken;
    }
  }

  return config;
}

/**
 * Interceptor to handle authentication rejections.
 *
 * @param error - The error object from the HTTP response.
 *
 * Uses as a response interceptor to catch authentication-related errors,
 * but would rethrow other error if not related to authentication.
 */
export function onRejectedAuthResponseInterceptor(error: any): any {
  // Add handling for authentication errors here, e.g., refresh access token
  // in the future.
  const [accessToken, refreshToken] = [
    Cookies.get(ACCESS_TOKEN_KEY),
    Cookies.get(REFRESH_TOKEN_KEY),
  ];

  // Add more here...

  return Promise.reject(error);
}

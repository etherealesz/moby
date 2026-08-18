import { InternalAxiosRequestConfig } from 'axios';
import { NetworkError } from '@/src/shared/errors';

/**
 * A global interceptor to be used in all HTTP requests.
 * It ensures that the request prepares the body and headers correctly.
 *
 * @param config The Axios request configuration.
 *
 * @returns The modified Axios request configuration.
 */
export function onFullFilledGlobalRequestInterceptor(
  config: InternalAxiosRequestConfig<any>
): InternalAxiosRequestConfig<any> {
  if (config.data) {
    const bodyContainsFormData = config.data instanceof FormData;
    if (!bodyContainsFormData) {
      config.headers.setContentType('application/json');

      // if (typeof config.data !== 'string') {
      //   config.data = JSON.stringify(config.data);
      // }
    }
  }

  return config;
}

/**
 * A global response interceptor to handle network errors.
 *
 * @param error The error object from the HTTP response.
 *
 * @returns A rejected promises.
 */
export function onRejectedGlobalResponseInterceptor(error: any) {
  if (!error.response) {
    return Promise.reject(new NetworkError());
  }
  return Promise.reject(error);
}

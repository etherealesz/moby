import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  CreateAxiosDefaults,
} from 'axios';
import {
  onFullFilledGlobalRequestInterceptor,
  onRejectedGlobalResponseInterceptor,
} from './interceptors/global';
import { TRequestInterceptorArgs, TResponseInterceptorArgs } from './type';

const DEFAULT_TIMEOUT_IN_MS = 10_000;

const defaultHttpClientConfig: CreateAxiosDefaults = {
  adapter: 'fetch',
  timeout: DEFAULT_TIMEOUT_IN_MS,
  validateStatus: (status) => status >= 200 && status < 300,
};

/**
 * Default configuration for the HTTP client used across the application.
 */
export const httpClient = axios.create(defaultHttpClientConfig);

interface IInterceptorsOptions {
  request?: TRequestInterceptorArgs[];
  response?: TResponseInterceptorArgs[];
}

interface ICustomHttpClientInterceptorsParams {
  interceptors?: IInterceptorsOptions;
}

/**
 * Generates a custom HTTP client by creating a new Axios instance
 * with the provided configuration and applying the specified interceptors.
 *
 * @param config - The Axios request configuration for the custom client.
 * @param interceptors - An object containing arrays of request and response
 *                       interceptors to be applied to the custom client.
 *
 * @returns A new Axios instance configured with the specified settings and
 *          interceptors.
 */
export function generateCustomHttpClient(
  config: AxiosRequestConfig,
  { interceptors }: ICustomHttpClientInterceptorsParams = {}
): AxiosInstance {
  const client = axios.create({
    ...defaultHttpClientConfig,
    ...config,
  });

  client.interceptors.request.use(onFullFilledGlobalRequestInterceptor);
  client.interceptors.response.use(
    undefined,
    onRejectedGlobalResponseInterceptor
  );

  interceptors?.request?.forEach((args) => {
    client.interceptors.request.use(...args);
  });
  interceptors?.response?.forEach((args) => {
    client.interceptors.response.use(...args);
  });

  return client;
}

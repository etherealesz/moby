import {
  AxiosInterceptorManager,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';

type TInterceptorArgs<T> = Parameters<AxiosInterceptorManager<T>['use']>;
type TRequestInterceptorArgs = TInterceptorArgs<InternalAxiosRequestConfig>;
type TResponseInterceptorArgs = TInterceptorArgs<AxiosResponse>;

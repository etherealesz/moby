import { TRequestInterceptorArgs, TResponseInterceptorArgs } from './type';

export function req(...args: TRequestInterceptorArgs): TRequestInterceptorArgs {
  return args;
}

export function res(
  ...args: TResponseInterceptorArgs
): TResponseInterceptorArgs {
  return args;
}

export function reqFullfilled(
  onFullfilled: TRequestInterceptorArgs[0],
  options?: TRequestInterceptorArgs[2]
): TRequestInterceptorArgs {
  return [onFullfilled, undefined, options];
}

export function resFullfilled(
  onFullfilled: TResponseInterceptorArgs[0]
): TResponseInterceptorArgs {
  return [onFullfilled, undefined];
}

export function reqRejected(
  onRejected: TRequestInterceptorArgs[1],
  options: TRequestInterceptorArgs[2]
): TRequestInterceptorArgs {
  return [undefined, onRejected, options];
}

export function resRejected(
  onRejected: TResponseInterceptorArgs[1]
): TResponseInterceptorArgs {
  return [undefined, onRejected];
}

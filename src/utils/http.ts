// This file is used to replace axios implementation with native fetch
export async function fetchClient(url: string, options: any) {
  const method = options?.method || 'GET';
  const headers = options?.headers || {};
  const body = options?.data ? JSON.stringify(options.data) : undefined;

  const response = await fetch(url, {
    method,
    headers,
    body,
    ...options
  });

  const data = await response.json().catch(() => null);

  return {
    data,
    status: response.status,
    statusText: response.statusText,
    headers: response.headers
  };
}

fetchClient.get = (url: string, options: any) => fetchClient(url, { ...options, method: 'GET' });
fetchClient.post = (url: string, data: any, options: any) => fetchClient(url, { ...options, method: 'POST', data });
fetchClient.put = (url: string, data: any, options: any) => fetchClient(url, { ...options, method: 'PUT', data });
fetchClient.delete = (url: string, options: any) => fetchClient(url, { ...options, method: 'DELETE' });
fetchClient.isAxiosError = (err: any) => err && !!err.isAxiosError;
fetchClient.interceptors = { request: { use: () => {}, eject: () => {} }, response: { use: () => {}, eject: () => {} } };
fetchClient.defaults = { proxy: undefined, httpAgent: undefined, httpsAgent: undefined };
fetchClient.create = () => fetchClient;
fetchClient.isCancel = () => false;

export type AxiosInstance = typeof fetchClient;
export type AxiosError = Error & { isAxiosError: boolean, config: any, response: any };
export type AxiosResponse<T = any> = { data: T, status: number, statusText: string, headers: any, config: any, request?: any };
export type AxiosRequestConfig = any;
export type AxiosLookupAddress = any;

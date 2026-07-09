// Пусто по умолчанию: запросы идут на свой origin (/api/...) и проксируются
// Vite на бэкенд. В проде задаётся через VITE_API_BASE.
export const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(status: number, detail?: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
    ...options,
  });

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = (await res.json()).detail;
    } catch {
      /* тело не JSON */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

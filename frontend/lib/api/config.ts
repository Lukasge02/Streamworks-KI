export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BACKEND_URL}${path}`;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail: unknown;
    try {
      const body = await response.json();
      detail = body.detail ?? body;
    } catch {
      detail = response.statusText;
    }

    throw new ApiError(
      `API request failed: ${response.status} ${response.statusText}`,
      response.status,
      detail
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

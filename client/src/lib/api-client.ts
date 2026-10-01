/**
 * HTTP client for the Mojo API, and the session state it depends on.
 *
 * - The access token is kept in memory only (never in storage).
 * - The refresh token lives in an httpOnly cookie that JS can't read; the browser sends it to
 *   /api/v1/auth/* when requests use `credentials: 'include'`.
 * - After a page load there is no access token until `refreshSession()` restores one from the
 *   cookie; `authFetch` does that automatically.
 *
 * Login, registration and logout live in `@/features/auth/session`, which starts and ends the
 * session through `applySession` and `clearSession`.
 */
import type { AccessTokenData, ErrorResponse, RefreshResponse } from '@/types/api.generated';

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const REFRESH_URL = `${API_BASE_URL}/api/v1/auth/refresh`;
const REFRESH_LEAD_SECONDS = 60;

let accessToken: string | null = null;
let refreshTimer: ReturnType<typeof setTimeout> | undefined;
let refreshInFlight: Promise<string | null> | null = null;


const isErrorResponse = (value: unknown): value is ErrorResponse =>
  !!value && typeof value === 'object' && 'businessCode' in value && 'message' in value;

// Accepts the ErrorResponse envelope, the same envelope nested under FastAPI's `detail`,
// or FastAPI's own `detail` (a string, or a list of validation errors).
export const getErrorMessage = async (response: Response, fallback: string) => {
  try {
    const payload: unknown = await response.json();
    const body = payload && typeof payload === 'object' && 'detail' in payload ? payload.detail : payload;
    if (isErrorResponse(body)) {
      return body.errors?.[0]?.message || body.message || fallback;
    }
    if (typeof body === 'string') {
      return body;
    }
    if (Array.isArray(body) && typeof body[0]?.msg === 'string') {
      return body[0].msg as string;
    }
    return fallback;
  } catch {
    return response.statusText || fallback;
  }
};

export const applySession = (data: AccessTokenData) => {
  accessToken = data.accessToken;
  clearTimeout(refreshTimer);
  // Refresh ahead of expiry so the in-memory token stays valid for callers of getToken().
  const delaySeconds = Math.max(data.expiresIn - REFRESH_LEAD_SECONDS, 5);
  refreshTimer = setTimeout(() => void refreshSession(), delaySeconds * 1000);
};

export const clearSession = () => {
  accessToken = null;
  clearTimeout(refreshTimer);
};

/** Current access token, or null before the session is restored. Prefer authFetch in new code. */
export const getToken = () => accessToken;

/** Exchange the refresh cookie for a new access token. Concurrent callers share one request. */
export const refreshSession = (): Promise<string | null> => {
  refreshInFlight ??= (async () => {
    try {
      const response = await fetch(REFRESH_URL, { method: 'POST', credentials: 'include' });
      if (!response.ok) {
        clearSession();
        return null;
      }
      const result = (await response.json()) as RefreshResponse;
      applySession(result.data);
      return accessToken;
    } catch {
      return null; // network error: keep the current state and let the caller retry
    } finally {
      refreshInFlight = null;
    }
  })();
  return refreshInFlight;
};

/** fetch() against the API with the access token attached; refreshes and retries once on 401. */
export const authFetch = async (path: string, init: RequestInit = {}): Promise<Response> => {
  const send = (token: string | null) => {
    const headers = new Headers(init.headers);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    return fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  };

  const token = accessToken ?? (await refreshSession());
  const response = await send(token);
  if (response.status !== 401) return response;

  const refreshed = await refreshSession();
  return refreshed ? send(refreshed) : response;
};

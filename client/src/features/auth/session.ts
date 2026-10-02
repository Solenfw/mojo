/**
 * Starting and ending a session: login, registration, logout and the current user.
 * The token handling itself lives in `@/lib/api-client`.
 */
import { API_BASE_URL, applySession, api, clearSession, getErrorMessage } from '@/lib/api-client';
import type {
  AccessTokenData,
  LoginRequest,
  LoginResponse,
  RegisterData,
  RegisterRequest,
  RegisterResponse,
  UserRead,
} from '@/types/api.generated';

const AUTH_URL = `${API_BASE_URL}/api/v1/auth`;

export const login = async (email: string, password: string): Promise<AccessTokenData> => {
  const response = await fetch(`${AUTH_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password } satisfies LoginRequest),
  });
  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Authentication failed'));
  }
  const result = (await response.json()) as LoginResponse;
  applySession(result.data);
  return result.data;
};

export const register = async (payload: RegisterRequest): Promise<RegisterData> => {
  const response = await fetch(`${AUTH_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to create account'));
  }
  const result = (await response.json()) as RegisterResponse;
  return result.data;
};

export const logout = async (): Promise<void> => {
  try {
    await fetch(`${AUTH_URL}/logout`, { method: 'POST', credentials: 'include' });
  } catch {
    // Signing out locally still matters if the server is unreachable.
  } finally {
    clearSession();
  }
};

export const getCurrentUser = async (): Promise<UserRead | null> => {
  try {
    const { data, response } = await api.GET('/api/v1/users/me');
    return response.ok && data ? data : null;
  } catch {
    return null;
  }
};

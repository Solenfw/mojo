const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'linguasphere_access_token';

export interface AuthToken {
  access_token: string;
  token_type: string;
  refresh_token?: string;
}

export interface CheckUserPayload {
  email?: string;
  phone?: string;
}

interface CurrentUser {
  id: number;
}

interface AuthPayload {
  emailOrPhone?: string;
  passwordHash: string;
  fullName?: string;
  email?: string;
  phone?: string;
  deviceId?: string;
  platform?: 'mobile' | 'web';
}

type ErrorBag = {
  message?: string;
  detail?: string;
  errors?: Array<{ message?: string }>;
};

const asErrorBag = (value: unknown): ErrorBag => {
  if (!value || typeof value !== 'object') {
    return {};
  }
  return value as ErrorBag;
};

const getErrorMessage = async (response: Response, fallback: string) => {
  try {
    const payload = asErrorBag(await response.json());
    const detail = typeof payload.detail === 'string' ? payload : asErrorBag(payload.detail);
    const firstError = Array.isArray(detail.errors) ? detail.errors[0] : null;
    return firstError?.message || detail.message || detail.detail || payload.message || fallback;
  } catch {
    return response.statusText || fallback;
  }
};

const authRequest = async (path: string, payload: AuthPayload): Promise<AuthToken> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Authentication failed'));
  }

  const result = await response.json();
  const data = result.data ?? {};
  return {
    access_token: data.accessToken,
    token_type: 'bearer',
    refresh_token: data.refreshToken,
  };
};

export const login = (emailOrPhone: string, password: string) => {
  return authRequest('/api/v1/auth/login', {
    emailOrPhone,
    passwordHash: password,
    platform: 'web',
  });
};

export const register = (email: string, password: string, fullName: string, phone: string) => {
  return authRequest('/api/v1/auth/register', {
    fullName: fullName.trim() || email.split('@')[0],
    email,
    phone: phone.trim(),
    passwordHash: password,
  });
};

export const checkUserByEmailOrPhone = async (payload: CheckUserPayload) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/check-user-by-email-or-phone`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (response.status === 409) {
    throw new Error(await getErrorMessage(response, 'User already exists'));
  }

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to validate account details'));
  }

  return response.json();
};

export const saveToken = (token: string) => {
  window.localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = () => {
  return window.localStorage.getItem(TOKEN_KEY);
};

export const clearToken = () => {
  window.localStorage.removeItem(TOKEN_KEY);
};

export const getCurrentUser = async () => {
  const token = getToken();
  if (!token) return null;

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch {
    clearToken();
    return null;
  }

  if (!response.ok) {
    clearToken();
    return null;
  }

  return (await response.json()) as CurrentUser;
};

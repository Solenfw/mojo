const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'linguasphere_access_token';

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface OnboardingPayload {
  level: string;
  goal: string;
  time: string;
}

export interface CheckUserPayload {
  email?: string;
  phone?: string;
}

interface AuthPayload {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
  phone?: string;
}

const authRequest = async (path: string, payload: AuthPayload): Promise<AuthToken> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = 'Authentication failed';
    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json();
};

export const login = (email: string, password: string) => {
  return authRequest('/api/v1/auth/login', { email, password });
};

export const register = (email: string, password: string, fullName?: string, phone?: string) => {
  const username = fullName?.trim() || email.split('@')[0];
  return authRequest('/api/v1/auth/register', {
    email,
    password,
    username,
    full_name: fullName?.trim() || undefined,
    phone: phone?.trim() || undefined,
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
    const error = await response.json();
    const detail = error.detail ?? error;
    const firstError = Array.isArray(detail.errors) ? detail.errors[0] : null;
    throw new Error(firstError?.message || detail.message || 'User already exists');
  }

  if (!response.ok) {
    let message = 'Unable to validate account details';
    try {
      const error = await response.json();
      const detail = error.detail ?? error;
      message = detail.message || detail.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
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

export const submitOnboarding = async (data: OnboardingPayload) => {
  const token = getToken();
  if (!token) {
    throw new Error('You need to log in again before finishing onboarding.');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let message = 'Unable to save onboarding preferences';
    try {
      const error = await response.json();
      const detail = error.detail ?? error;
      message = detail.message || detail.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json();
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

  return response.json();
};

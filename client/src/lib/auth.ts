const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const TOKEN_KEY = 'linguasphere_access_token';

export interface AuthToken {
  access_token: string;
  token_type: string;
}

interface AuthPayload {
  email: string;
  password: string;
  username?: string;
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

export const register = (email: string, password: string, username?: string) => {
  return authRequest('/api/v1/auth/register', { email, password, username });
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

  return response.json();
};

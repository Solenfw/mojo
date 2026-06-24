import { getCurrentUser, getToken } from '@/lib/auth';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export interface OnboardingPayload {
  level: string;
  goal: string;
  time: string;
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

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
});

const submitOnboardingLegacy = async (token: string, data: OnboardingPayload) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/submit`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to save onboarding preferences'));
  }

  return response.json();
};

export const submitOnboarding = async (data: OnboardingPayload) => {
  const token = getToken();
  if (!token) {
    throw new Error('You need to log in again before finishing onboarding.');
  }

  const currentUser = await getCurrentUser();
  if (!currentUser) {
    throw new Error('You need to log in again before finishing onboarding.');
  }

  const sessionResponse = await fetch(`${API_BASE_URL}/api/v1/onboarding/session`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      userId: currentUser.id,
      sessionToken: token,
    }),
  });

  if (!sessionResponse.ok) {
    if (sessionResponse.status === 409) {
      return submitOnboardingLegacy(token, data);
    }
    throw new Error(await getErrorMessage(sessionResponse, 'Unable to start onboarding.'));
  }

  const sessionResult = await sessionResponse.json();
  const sessionId = sessionResult.data?.sessionId;
  if (!sessionId) {
    throw new Error('Unable to start onboarding.');
  }

  const answers = [
    { questionCode: 'starting_level', answerValue: data.level },
    { questionCode: 'goal', answerValue: data.goal },
    { questionCode: 'time', answerValue: data.time },
  ];

  for (const answer of answers) {
    const answerResponse = await fetch(`${API_BASE_URL}/api/v1/onboarding/answers`, {
      method: 'POST',
      headers: getAuthHeaders(token),
      body: JSON.stringify({
        sessionId,
        questionCode: answer.questionCode,
        answerValue: answer.answerValue,
      }),
    });

    if (!answerResponse.ok) {
      throw new Error(await getErrorMessage(answerResponse, 'Unable to save onboarding answer.'));
    }
  }

  const finalizeResponse = await fetch(`${API_BASE_URL}/api/v1/onboarding/session/finalize`, {
    method: 'PUT',
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      sessionId,
      sessionToken: token,
    }),
  });

  if (!finalizeResponse.ok) {
    throw new Error(await getErrorMessage(finalizeResponse, 'Unable to finalize onboarding.'));
  }

  const onboardedResponse = await fetch(`${API_BASE_URL}/api/v1/users/onboarding/complete`, {
    method: 'PUT',
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      userId: currentUser.id,
      sessionToken: token,
    }),
  });

  if (!onboardedResponse.ok) {
    if (onboardedResponse.status === 409) {
      return finalizeResponse.json();
    }
    throw new Error(await getErrorMessage(onboardedResponse, 'Unable to complete onboarding.'));
  }

  return onboardedResponse.json();
};

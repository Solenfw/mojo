import { authFetch, getErrorMessage } from '@/lib/auth';
import type { OnboardingData, OnboardingRequest, OnboardingResponse } from '@/types/api.generated';

export const submitOnboarding = async (answers: OnboardingRequest): Promise<OnboardingData> => {
  const response = await authFetch('/api/v1/onboarding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(answers),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to save your onboarding answers.'));
  }

  const result = (await response.json()) as OnboardingResponse;
  return result.data;
};

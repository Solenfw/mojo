import { api, unwrap } from '@/lib/api-client';
import type { OnboardingData, OnboardingRequest } from '@/types/api.generated';

export const submitOnboarding = async (answers: OnboardingRequest): Promise<OnboardingData> =>
  unwrap(await api.POST('/api/v1/onboarding', { body: answers }), 'Unable to save your onboarding answers.').data;

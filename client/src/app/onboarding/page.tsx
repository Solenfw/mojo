'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { OnboardingView } from '@/features/onboarding/onboarding-view';
import { AuthGuard } from '@/features/auth/auth-guard';
import { submitOnboarding } from '@/features/onboarding/api';
import type { OnboardingRequest } from '@/types/api.generated';

export default function OnboardingPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = async (data: OnboardingRequest) => {
    setIsSubmitting(true);
    setError(null);
    try {
      await submitOnboarding(data);
      router.push('/dashboard');
    } catch (err) {
      console.error('Failed to submit onboarding', err);
      setError(err instanceof Error ? err.message : 'Unable to save your onboarding setup right now.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthGuard>
      <OnboardingView
        onComplete={handleComplete}
        onSkip={() => router.push('/dashboard')}
        isSubmitting={isSubmitting}
        error={error}
      />
    </AuthGuard>
  );
}

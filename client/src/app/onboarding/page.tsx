'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Onboarding } from '@/features/auth/components/onboarding';
import { AuthGuard } from '@/features/auth/components/auth-guard';
import { submitOnboarding } from '@/lib/auth';

export default function OnboardingPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = async (data: { level: string; goal: string; time: string }) => {
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
      <Onboarding
        onComplete={handleComplete}
        onSkip={() => router.push('/dashboard')}
        isSubmitting={isSubmitting}
        error={error}
      />
    </AuthGuard>
  );
}

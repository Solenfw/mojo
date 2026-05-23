'use client';

import { useRouter } from 'next/navigation';
import { Onboarding } from '@/features/auth/components/onboarding';
import { AuthGuard } from '@/features/auth/components/auth-guard';

export default function OnboardingPage() {
  const router = useRouter();

  return (
    <AuthGuard>
      <Onboarding onComplete={() => router.push('/dashboard')} />
    </AuthGuard>
  );
}

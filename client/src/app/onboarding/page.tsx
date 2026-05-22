'use client';

import { useRouter } from 'next/navigation';
import { Onboarding } from '@/features/auth/components/onboarding';

export default function OnboardingPage() {
  const router = useRouter();

  return <Onboarding onComplete={() => router.push('/dashboard')} />;
}

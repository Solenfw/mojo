'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { AuthLayout, SignUpForm } from '@/features/auth/components/auth-pages';

export default function SignUpPage() {
  const router = useRouter();

  const handleAuthSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    router.push('/onboarding');
  };

  return (
    <AuthLayout title="Start Journey" subtitle="Create your account to unlock AI powered learning" onBack={() => router.push('/')}>
      <SignUpForm onSubmit={handleAuthSubmit} onLogin={() => router.push('/login')} />
    </AuthLayout>
  );
}

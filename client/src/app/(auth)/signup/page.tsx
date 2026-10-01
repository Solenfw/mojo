'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { AuthLayout, SignUpForm } from '@/features/auth/login-form';
import { register, login } from '@/features/auth/session';

export default function SignUpPage() {
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleAuthSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const fullName = (formData.get('fullName') as string).trim();
    const username = (formData.get('username') as string).trim();
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      await register({ username, fullName, email, password });
      await login(email, password);
      router.push('/onboarding');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title="Start Journey" subtitle="Create your account to unlock AI powered learning" onBack={() => router.push('/')}>
      <SignUpForm
        onSubmit={handleAuthSubmit}
        onLogin={() => router.push('/login')}
        error={error}
        isLoading={isLoading}
      />
    </AuthLayout>
  );
}

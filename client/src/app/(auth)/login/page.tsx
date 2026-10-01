// client/src/app/(auth)/login/page.tsx
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { AuthLayout } from '@/features/auth/auth-layout';
import { LoginForm } from '@/features/auth/login-form';
import { login, getCurrentUser } from '@/features/auth/session';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleAuthSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      await login(email, password);
      
      // Fetch the user to check if they have completed onboarding
      const user = await getCurrentUser();
      
      if (user?.isOnboarded) {
        router.push('/dashboard');
      } else {
        router.push('/onboarding');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title="Welcome Back" subtitle="Sign in to continue your path to mastery" onBack={() => router.push('/')}>
      <LoginForm 
        onSubmit={handleAuthSubmit} 
        onSignUp={() => router.push('/signup')} 
        onForgotPassword={() => router.push('/forgot-password')}
        error={error}
        isLoading={isLoading}
      />
    </AuthLayout>
  );
}
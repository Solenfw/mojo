// client/src/app/(auth)/login/page.tsx
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { AuthLayout, LoginForm } from '@/features/auth/components/auth-pages';
import { login, saveToken, getCurrentUser } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      const token = await login(email, password);
      saveToken(token.access_token);
      
      // Fetch the user to check if they have completed onboarding
      const user = await getCurrentUser();
      
      if (user?.is_onboarded) {
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
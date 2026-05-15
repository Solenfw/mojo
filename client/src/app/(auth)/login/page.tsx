'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { AuthLayout, LoginForm } from '@/features/auth/components/auth-pages';

export default function LoginPage() {
  const router = useRouter();

  const handleAuthSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    if (email === 'admin' && password === 'admin123') {
      router.push('/admin');
    } else {
      router.push('/onboarding');
    }
  };

  return (
    <AuthLayout title="Welcome Back" subtitle="Sign in to continue your path to mastery" onBack={() => router.push('/')}>
      <LoginForm 
        onSubmit={handleAuthSubmit} 
        onSignUp={() => router.push('/signup')} 
        onForgotPassword={() => router.push('/forgot-password')} 
      />
    </AuthLayout>
  );
}

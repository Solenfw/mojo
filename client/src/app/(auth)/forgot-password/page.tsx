'use client';

import { useRouter } from 'next/navigation';
import { AuthLayout } from '@/features/auth/auth-layout';
import { ForgotPasswordForm } from '@/features/auth/forgot-password-form';

export default function ForgotPasswordPage() {
  const router = useRouter();

  return (
    <AuthLayout title="Reset Password" subtitle="We'll help you get back into your account" onBack={() => router.push('/login')}>
      <ForgotPasswordForm onBack={() => router.push('/login')} />
    </AuthLayout>
  );
}

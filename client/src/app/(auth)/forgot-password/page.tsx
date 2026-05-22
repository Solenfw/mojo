'use client';

import { useRouter } from 'next/navigation';
import { AuthLayout, ForgotPasswordForm } from '@/features/auth/components/auth-pages';

export default function ForgotPasswordPage() {
  const router = useRouter();

  return (
    <AuthLayout title="Reset Password" subtitle="We'll help you get back into your account" onBack={() => router.push('/login')}>
      <ForgotPasswordForm onBack={() => router.push('/login')} />
    </AuthLayout>
  );
}

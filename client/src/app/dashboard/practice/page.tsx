'use client';

import { useRouter } from 'next/navigation';
import { KaiwaPractice } from '@/features/practice/components/kaiwa-practice';

export default function PracticePage() {
  const router = useRouter();

  return <KaiwaPractice onBack={() => router.push('/dashboard')} />;
}

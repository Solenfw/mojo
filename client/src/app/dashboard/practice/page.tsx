'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { KaiwaPractice } from '@/features/conversation/components/kaiwa-practice';

export default function PracticePage() {
  const router = useRouter();

  return <KaiwaPractice onBack={() => router.push('/dashboard')} />;
}

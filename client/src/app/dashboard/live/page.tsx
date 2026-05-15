'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { LiveCall } from '@/features/conversation/components/live-call';

export default function LivePage() {
  const router = useRouter();

  return <LiveCall onBack={() => router.push('/dashboard')} />;
}

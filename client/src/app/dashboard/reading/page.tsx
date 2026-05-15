'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Reading } from '@/features/reading/components/reading-view';

export default function ReadingPage() {
  const router = useRouter();

  return <Reading onBack={() => router.push('/dashboard')} />;
}

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { KanjiCanvas } from '@/features/kanji/components/kanji-canvas';

export default function WritingPage() {
  const router = useRouter();

  return <KanjiCanvas onBack={() => router.push('/dashboard')} />;
}

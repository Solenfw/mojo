'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Vocabulary } from '@/features/vocab/components/vocabulary-view';

export default function VocabularyPage() {
  const router = useRouter();

  return <Vocabulary onBack={() => router.push('/dashboard')} />;
}

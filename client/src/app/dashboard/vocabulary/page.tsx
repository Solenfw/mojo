'use client';

import { useRouter } from 'next/navigation';
import { Vocabulary } from '@/features/vocabulary/components/vocabulary-view';

export default function VocabularyPage() {
  const router = useRouter();
  return <Vocabulary onBack={() => router.push('/dashboard')} />;
}

'use client';

import { useRouter } from 'next/navigation';
import { KanjiCanvas } from '@/features/writing/kanji-canvas';

export default function WritingPage() {
  const router = useRouter();

  return <KanjiCanvas onBack={() => router.push('/dashboard')} />;
}

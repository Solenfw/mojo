'use client';

import { useRouter } from 'next/navigation';
import { LiveCall } from '@/features/conversation/components/live-call';

export default function LivePage() {
  const router = useRouter();

  return <LiveCall onBack={() => router.push('/dashboard')} />;
}

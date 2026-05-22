'use client';

import { useRouter } from 'next/navigation';
import { AdminDashboard } from '@/features/admin/components/admin-dashboard';

export default function AdminPage() {
  const router = useRouter();

  return <AdminDashboard onSignOut={() => router.push('/')} />;
}

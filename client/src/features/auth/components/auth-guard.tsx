'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

import { getCurrentUser } from '@/lib/auth';

export const AuthGuard = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const [isChecking, setIsChecking] = React.useState(true);

  React.useEffect(() => {
    let active = true;

    const verifySession = async () => {
      const user = await getCurrentUser();
      if (!active) return;

      if (!user) {
        router.replace('/login');
        return;
      }

      setIsChecking(false);
    };

    verifySession();

    return () => {
      active = false;
    };
  }, [router]);

  if (isChecking) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm font-medium text-muted-foreground">
        Loading session...
      </div>
    );
  }

  return children;
};

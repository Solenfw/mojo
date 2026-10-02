import { api, unwrap } from '@/lib/api-client';
import type { DashboardData } from '@/types/api.generated';

export const getDashboard = async (): Promise<DashboardData> =>
  unwrap(await api.GET('/api/v1/users/me/dashboard'), 'Unable to load your dashboard.').data;

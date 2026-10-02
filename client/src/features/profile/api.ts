import { api, unwrap } from '@/lib/api-client';
import type { ProfileData } from '@/types/api.generated';

export const getProfile = async (): Promise<ProfileData> =>
  unwrap(await api.GET('/api/v1/users/me/profile'), 'Unable to load your profile.').data;

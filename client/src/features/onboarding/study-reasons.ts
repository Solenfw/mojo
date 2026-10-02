import { Briefcase, GraduationCap, House, Plane, Sparkles, Tv } from 'lucide-react';
import type { OnboardingRequest } from '@/types/api.generated';

type StudyReason = OnboardingRequest['studyReason'];

export const STUDY_REASONS: { id: StudyReason; title: string; desc: string; icon: typeof Plane }[] = [
  { id: 'travel', title: 'Travel', desc: 'Get around and talk with people on my trips.', icon: Plane },
  { id: 'work', title: 'Work', desc: 'Use Japanese in my job or career.', icon: Briefcase },
  { id: 'anime_manga', title: 'Anime & Manga', desc: 'Enjoy shows, manga and games in Japanese.', icon: Tv },
  { id: 'jlpt', title: 'Pass the JLPT', desc: 'Get certified and track my progress.', icon: GraduationCap },
  { id: 'living_in_japan', title: 'Living in Japan', desc: 'Handle daily life in Japan.', icon: House },
  { id: 'other', title: 'Something Else', desc: 'I have my own reasons.', icon: Sparkles },
];

/** Display name for a stored study reason code (the profile returns it as a plain string). */
export const studyReasonLabel = (code: string | null): string | null =>
  STUDY_REASONS.find((reason) => reason.id === code)?.title ?? code;

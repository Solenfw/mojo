import { api, unwrap } from '@/lib/api-client';
import type { SrsReviewData, SrsReviewRequest, VocabularyRead } from '@/types/api.generated';

/** Cards due now; a card enters the schedule the first time it is reviewed. */
export const getReviewQueue = async (): Promise<VocabularyRead[]> =>
  unwrap(await api.GET('/api/v1/vocabulary/review-queue'), 'Unable to load your review queue.').data;

export const getLessonVocabulary = async (lessonId: number): Promise<VocabularyRead[]> =>
  unwrap(await api.GET('/api/v1/vocabulary', { params: { query: { lessonId } } }), 'Unable to load vocabulary.').data;

export const reviewCard = async (vocabId: number, result: SrsReviewRequest['result']): Promise<SrsReviewData> =>
  unwrap(await api.POST('/api/v1/vocabulary/reviews', { body: { vocabId, result } }), 'Unable to save your review.').data;

import { api, unwrap } from '@/lib/api-client';
import type { EvaluateWritingData, EvaluateWritingRequest, KanjiPracticeRead } from '@/types/api.generated';

export const getKanjiPractice = async (practiceId: number): Promise<KanjiPracticeRead> =>
	unwrap(
		await api.GET('/api/v1/writing/kanji/{practice_id}', { params: { path: { practice_id: practiceId } } }),
		'Unable to load the kanji practice.',
	).data;

export const evaluateWriting = async (body: EvaluateWritingRequest): Promise<EvaluateWritingData> =>
	unwrap(await api.POST('/api/v1/writing/evaluations', { body }), 'Unable to evaluate your writing.').data;

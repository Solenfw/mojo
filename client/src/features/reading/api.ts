import { api, unwrap } from '@/lib/api-client';
import type {
	ReadingPassageRead,
	SubmitReadingAttemptData,
	SubmitReadingAttemptRequest,
} from '@/types/api.generated';

export const getPassage = async (passageId: number): Promise<ReadingPassageRead> =>
	unwrap(
		await api.GET('/api/v1/reading/passages/{passage_id}', { params: { path: { passage_id: passageId } } }),
		'Unable to load the reading passage.',
	).data;

export const submitReadingAttempt = async (
	body: SubmitReadingAttemptRequest,
): Promise<SubmitReadingAttemptData> =>
	unwrap(await api.POST('/api/v1/reading/attempts', { body }), 'Unable to submit your reading attempt.').data;

import { api, unwrap } from '@/lib/api-client';
import type {
	DialogueRead,
	RatePronunciationRequest,
	RatePronunciationResponse,
	SubmitDialogueAttemptData,
	SubmitDialogueAttemptRequest,
} from '@/types/api.generated';

export const getDialogue = async (dialogueId: number): Promise<DialogueRead> =>
	unwrap(
		await api.GET('/api/v1/speaking/dialogues/{dialogue_id}', { params: { path: { dialogue_id: dialogueId } } }),
		'Unable to load the dialogue.',
	).data;

export const ratePronunciation = async (body: RatePronunciationRequest): Promise<RatePronunciationResponse> =>
	unwrap(await api.POST('/api/v1/speaking/pronunciation', { body }), 'Unable to rate your pronunciation.');

export const submitDialogueAttempt = async (
	body: SubmitDialogueAttemptRequest,
): Promise<SubmitDialogueAttemptData> =>
	unwrap(await api.POST('/api/v1/speaking/attempts', { body }), 'Unable to submit your dialogue attempt.').data;

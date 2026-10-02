# Client API layer: conventions

## The layers

```
features/<name>/<name>-view.tsx     UI only: state, rendering, mapping data to view shapes
        │  calls
        ▼
features/<name>/api.ts              one typed function per endpoint the feature uses
        │  calls
        ▼
lib/api-client.ts                   `api` (typed client), `unwrap`, `ApiError`, session/token handling
        │  uses
        ▼
types/api.generated.ts              generated from openapi.json; never edited by hand
```

## Rules

1. **Components never call `fetch`, `api` or `authFetch` directly.** They import functions from their feature's `api.ts`. The only exceptions are `lib/api-client.ts` and `features/auth/session.ts`. Login, register and logout must not carry a bearer token, so they keep using plain `fetch`.
2. **Every call goes through the typed `api` client.** The path, method, path params, query params and request body are all checked against `openapi.json`. Calling a route that doesn't exist, or sending `vocab_id` instead of `vocabId`, is a compile error.
3. **Wire types come from `@/types/api.generated` only.** Use the root aliases, such as `ProfileData` and `VocabularyRead`. Never hand-write a type for data that crosses the wire. If the UI needs a different shape, define that type in the component file and map to it there.
4. **`api.ts` functions return contract data unchanged.** For enveloped responses (`{ success, data, ... }`) they return `.data`. For the few routes that aren't enveloped (`/users/me`, `/speaking/pronunciation`, `/speaking/kaiwa`) they return the body. They don't reshape data for the UI.
5. **On failure, `api.ts` functions throw `ApiError`.** It carries the server's message and the HTTP status. Components catch it, show `error.message`, and `console.error` anything unexpected.
6. **The server computes scores and XP.** The client never sends a score or XP and never adds XP up itself. It shows the `xpEarned` the server returns.
7. **Features may import another feature's `api.ts`, never its components.** The main example is `features/curriculum/api.ts`, which owns levels, courses and lessons and is shared by every practice screen.
8. **Naming.** Functions start with a verb: `get*`, `submit*`, `review*`, `rate*`, `evaluate*`. Path params keep the server's names (`{ lesson_id: id }`). Query params and bodies are camelCase.
9. **Contract changes start on the server.** Change the schema, run `make api-types`, commit `openapi.json` and `api.generated.ts`, then run `npm run type-check`. The compiler lists every call site that broke.

## What an `api.ts` looks like

```ts
// features/vocabulary/api.ts
import { api, unwrap } from '@/lib/api-client';
import type { SrsReviewData, SrsReviewRequest, VocabularyRead } from '@/types/api.generated';

export const getReviewQueue = async (): Promise<VocabularyRead[]> =>
  unwrap(await api.GET('/api/v1/vocabulary/review-queue'), 'Unable to load your review queue.').data;

export const getLessonVocabulary = async (lessonId: number): Promise<VocabularyRead[]> =>
  unwrap(await api.GET('/api/v1/vocabulary', { params: { query: { lessonId } } }), 'Unable to load vocabulary.').data;

export const reviewCard = async (vocabId: number, result: SrsReviewRequest['result']): Promise<SrsReviewData> =>
  unwrap(await api.POST('/api/v1/vocabulary/reviews', { body: { vocabId, result } }), 'Unable to save your review.').data;
```

Path params and a route that isn't enveloped:

```ts
export const getLesson = async (lessonId: number): Promise<LessonDetailRead> =>
  unwrap(
    await api.GET('/api/v1/lessons/{lesson_id}', { params: { path: { lesson_id: lessonId } } }),
    'Unable to load the lesson.',
  ).data;

// Not enveloped: the body is the result itself.
export const ratePronunciation = async (body: RatePronunciationRequest): Promise<RatePronunciationResponse> =>
  unwrap(await api.POST('/api/v1/speaking/pronunciation', { body }), 'Unable to rate your pronunciation.');
```

In a component:

```ts
useEffect(() => {
  getProfile()
    .then(setProfile)
    .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load your profile.'))
    .finally(() => setLoading(false));
}, []);
```

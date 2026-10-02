# Client API layer: conventions and porting plan

This document has two parts:

- **Part 1, Conventions** is permanent. It describes how the client talks to the API.
- **Part 2, Porting plan** is temporary. It is the step-by-step plan for moving every screen onto the current API contract. Delete it once the last step is done.

## Why this exists

The server was redesigned (camelCase JSON, enveloped responses, new routes), but most screens still call the old API:

| Screen | State today |
|---|---|
| Profile, dashboard home | The endpoint exists, but the component reads the old response shape (`profile.study_goal` instead of `data.studyIntention`), so it shows nothing real. |
| Vocabulary, reading, practice, writing | They call routes that no longer exist (`/courses/by-level`, `/srs/due`, `/lessons/{id}/reading`, `/speaking/evaluate`, `/writing/evaluate`, ...), so they get 404s. |
| Onboarding, auth, settings | Already on the contract. |

These screens kept compiling because each one used raw `fetch` with hand-written types. The compiler had no way to know the contract had changed. The plan below fixes that first, then ports each screen.

---

# Part 1: Conventions

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

---

# Part 2: Porting plan

Work through the steps in order. Each step is one commit, or a few, on its own branch or stacked on the previous one. A step is done when everything under "Verify every step" passes.

| Step | Scope | Depends on |
|---|---|---|
| 0 | Foundation: `openapi-fetch`, `api`, `unwrap`, `ApiError`; onboarding and `getCurrentUser` as the first users | — |
| 1 | Profile | 0 |
| 2 | Dashboard home → `features/dashboard/` | 0, 3 |
| 3 | Curriculum `api.ts` (no UI) | 0 |
| 4 | Vocabulary | 3 |
| 5 | Reading | 3, 4 (for the glossary) |
| 6 | Practice (kaiwa) | 3 |
| 7 | Writing | 3 |
| 8 | Clean-up | all |

Steps 2 and 3 can be done in either order. Doing 3 first is simpler, because the dashboard's lesson list needs it.

## Verify every step

1. `npm run type-check`, `npm run build` and `npm run lint` all pass. Lint still fails on code nobody has touched yet (see Step 8). Each step must not add new lint problems, and the files it touches should end up lint-clean.
2. Run it for real. Run `make dev` (database and API) in one terminal and `make client-dev` in another. Sign in, open the screen, and do its main flow. In DevTools → Network, every call should return 2xx and carry an `Authorization` header.
3. Check the database side effects, such as XP going up after a passed attempt. The dashboard's activity chart is the quickest place to see this.
4. Remove the hand-written types the step stopped using from `src/types/index.ts`, plus the `getToken` / `API_BASE_URL` imports from the component.

## Step 0: Foundation

**Goal:** a typed client that every later step builds on.

1. `npm install openapi-fetch` (0.17.x). It comes from the same project as `openapi-typescript` and reads the `paths` type that `npm run gen:api` already generates.
2. In `lib/api-client.ts`:
   - Split `getErrorMessage` so its parsing can work on a body that has already been read:
     ```ts
     export const errorMessageFrom = (payload: unknown, fallback: string): string => {
       const body = payload && typeof payload === 'object' && 'detail' in payload ? payload.detail : payload;
       if (isErrorResponse(body)) return body.errors?.[0]?.message || body.message || fallback;
       if (typeof body === 'string' && body) return body;
       if (Array.isArray(body) && typeof body[0]?.msg === 'string') return body[0].msg as string;
       return fallback;
     };

     export const getErrorMessage = async (response: Response, fallback: string) => {
       try {
         return errorMessageFrom(await response.json(), fallback);
       } catch {
         return response.statusText || fallback;
       }
     };
     ```
   - Replace `authFetch`'s body with a version that takes a `Request`, which is the form `openapi-fetch` hands to a custom `fetch`. Then create the client:
     ```ts
     import createClient from 'openapi-fetch';
     import type { paths } from '@/types/api.generated';

     /** Sends the request with the access token attached; refreshes and retries once on 401. */
     const sendWithAuth = async (request: Request): Promise<Response> => {
       const retry = request.clone(); // a request body can only be read once
       const send = (req: Request, token: string | null) => {
         if (token) req.headers.set('Authorization', `Bearer ${token}`);
         return fetch(req);
       };

       const response = await send(request, accessToken ?? (await refreshSession()));
       if (response.status !== 401) return response;

       const refreshed = await refreshSession();
       return refreshed ? send(retry, refreshed) : response;
     };

     /** Typed client for the API contract: paths, params and bodies are checked against openapi.json. */
     export const api = createClient<paths>({ baseUrl: API_BASE_URL, fetch: sendWithAuth });

     export class ApiError extends Error {
       constructor(message: string, readonly status: number) {
         super(message);
         this.name = 'ApiError';
       }
     }

     /** The body of a successful call; otherwise throws an ApiError with the server's message. */
     export const unwrap = <T>(result: { data?: T; error?: unknown; response: Response }, fallback: string): T => {
       if (!result.response.ok) {
         throw new ApiError(errorMessageFrom(result.error, fallback), result.response.status);
       }
       return result.data as T;
     };
     ```
3. Move the existing users onto it, as the reference implementations:
   - Replace `features/onboarding/submit-onboarding.ts` with `features/onboarding/api.ts`, which exports `submitOnboarding(body: OnboardingRequest): Promise<OnboardingData>` using `api.POST('/api/v1/onboarding', { body })`. Update the import in `app/onboarding/page.tsx`.
   - Change `getCurrentUser` in `features/auth/session.ts` to use the typed client. It keeps its current contract: `UserRead | null`, and it never throws.
     ```ts
     export const getCurrentUser = async (): Promise<UserRead | null> => {
       try {
         const { data, response } = await api.GET('/api/v1/users/me');
         return response.ok && data ? data : null;
       } catch {
         return null;
       }
     };
     ```
4. Delete `authFetch` once nothing imports it. Keep `getToken` until Step 8, because unported screens still use it.

**Done when** login, onboarding, settings and the auth guard work as before. Checking Network after a hard reload should show `POST /auth/refresh` first, then `/users/me` carrying the `Authorization` header.

> Every code snippet and `api.ts` signature in this document was type-checked against the current `api.generated.ts` with `openapi-fetch` 0.17.0. A removed route, a snake_case body field, a bad enum value and a missing path param each fail to compile.

## Step 1: Profile

`features/profile/api.ts`: `getProfile(): Promise<ProfileData>` → `GET /api/v1/users/me/profile`.

| UI reads today | Contract (`ProfileData`) | Note |
|---|---|---|
| `name`, `email`, `xp`, `streak`, `avatarUrl` | same | — |
| `current_level` | `currentLevel` | nullable ("not set") |
| `target_level` | `targetLevel` | nullable |
| `member_since` | `memberSince` | ISO datetime; format with `toLocaleDateString` |
| `study_goal` | `studyIntention` | A reason code (`anime_manga`, ...). Show its label. The labels are in `onboarding-view.tsx` (`reasons`); move them to `features/onboarding/study-reasons.ts` and import them in both places. |
| `phone` | — | Not in the contract. Replace the row with "Daily goal: `dailyStudyMinutes` min". |

`WEEKLY_PLAN` stays mock data. There's no endpoint for it yet.

## Step 2: Dashboard home → `features/dashboard/`

1. `git mv` is the wrong tool here: the route file has to stay. Instead, create `features/dashboard/dashboard-view.tsx` and move `DashboardContent` and the `motion.div` wrapper into it, exported as `DashboardView`. `app/dashboard/page.tsx` becomes a thin route like the others:
   ```tsx
   import { DashboardView } from '@/features/dashboard/dashboard-view';
   export default function DashboardPage() {
     return <DashboardView />;
   }
   ```
   Commit this move on its own, before changing any behavior.
2. `features/dashboard/api.ts`: `getDashboard(): Promise<DashboardData>` → `GET /api/v1/users/me/dashboard`.

| UI reads today | Contract (`DashboardData`) | Note |
|---|---|---|
| `user.name`, `user.streak`, `user.level` | `user.*` | `level` is nullable |
| `activity[]` (`day`, `xp`) | `activity[]` (`day`, `xp`) | `day` is an ISO date (`2026-10-01`). Format it as a weekday for the chart's X axis. |
| `mastery[]` (`module`, `score` %) | `skills[]` (`skill`, `xp`) | **The meaning changes: XP per skill, not a percentage.** Show the XP and draw each bar relative to the top skill (`xp / maxXp * 100`). Map the codes `vocab`, `reading`, `speaking`, `writing`, `listening` to display names. |
| `N5_LESSONS` (mock) | `getLevelLessons('N5')` from Step 3 | Show `title` and `estimatedMinutes`. `xpReward` and `description` don't exist on lessons. When a lesson is clicked, open the first practice it contains: reading passages → `/dashboard/reading`, dialogues → `/dashboard/practice`, kanji → `/dashboard/writing`, otherwise `/dashboard/vocabulary`. |

## Step 3: Curriculum `api.ts` (no UI)

`features/curriculum/api.ts` owns the curriculum tree that every practice screen browses:

```ts
getLevels(): Promise<ProficiencyLevelRead[]>                 // GET /levels
getCourses(levelId?: number): Promise<CourseRead[]>          // GET /courses?levelId=
getLessons(courseId: number): Promise<LessonRead[]>          // GET /courses/{course_id}/lessons
getLesson(lessonId: number): Promise<LessonDetailRead>       // GET /lessons/{lesson_id}

/** Lessons of the first course at a level, with what each contains. */
export const getLevelLessons = async (levelName: string): Promise<LessonDetailRead[]> => {
  const level = (await getLevels()).find((item) => item.name === levelName);
  if (!level) return [];
  const [course] = await getCourses(level.id);
  if (!course) return [];
  const lessons = await getLessons(course.id);
  return Promise.all(lessons.map((lesson) => getLesson(lesson.id)));
};
```

This replaces the old `courses/by-level` + `courses/lessons` pair that reading and vocabulary each copied.

- **Which level:** keep `'N5'` hard-coded, as the screens do today. Using the learner's own level comes later.
- **Lessons no longer have a type.** The old client filtered on `lessonType === 'vocabulary' | 'reading'`. Now a lesson *contains* practices. A screen filters `LessonDetailRead` on `vocabularyCount > 0`, `readingPassages.length`, `dialogues.length` or `kanjiPractices.length`.
- **Cost:** `getLevelLessons` makes one request per lesson. That's fine for a single N5 course, but see gap G1.

## Step 4: Vocabulary

`features/vocabulary/api.ts`: `getReviewQueue`, `getLessonVocabulary`, `reviewCard` (shown in Part 1).

| Old call | New call |
|---|---|
| `GET /srs/due` (deck count and SRS cards) | `getReviewQueue()`. Fetch it once: its length is the deck count and its items are the cards. |
| `courses/by-level` + `courses/lessons`, filtered on `lessonType` | `getLevelLessons('N5')` filtered on `vocabularyCount > 0`. `totalItems = vocabularyCount`, a real count instead of the old `estimatedDuration` guess. |
| `GET /lessons/{id}/vocabulary` | `getLessonVocabulary(lessonId)` |
| `POST /srs/review` `{ vocab_id, quality_score }` | `reviewCard(vocabId, result)` |
| `POST /lessons/{id}/complete` `{ xp_gained, vocab_learned }` | **Removed.** There is no lesson-completion endpoint. XP is earned per review. |

- **Card mapping** (`VocabularyRead` → the component's card type): `id` → `id`, `kana` → `vocab`, `kanji` → `kanji` (only when it differs from `kana`), `romaji`, `meaning`, `exampleSentence` → `example`, `exampleTranslation` → `exampleMeaning`. Drop the `Math.random()` id fallback, because ids are always present now.
- **Buttons:** Forgot → `'again'`, Hard → `'hard'`, Easy → `'easy'`. These match the server's `QUALITY_BY_RESULT` (1, 3, 5), so behavior is unchanged.
- **Behavior change:** lesson decks now call `reviewCard` too. That's how a new card enters the SRS schedule ("New cards enter the schedule the first time they are reviewed"). Previously only SRS decks posted reviews.
- **Behavior change:** session XP is the sum of `xpEarned` from the responses, not the client's `+10 / +2`. Reviewing a card before it's due earns 0.
- **Types:** replace `VocabularyDeck` (with its `'srs_due'` string id) by a local union, `{ kind: 'srs' } | { kind: 'lesson'; lessonId: number; title: string; count: number }`. Delete `VocabularyDeck` and `NormalizedCard` from `types/index.ts`.

## Step 5: Reading

`features/reading/api.ts`:

```ts
getPassage(passageId: number): Promise<ReadingPassageRead>                                // GET /reading/passages/{passage_id}
submitReadingAttempt(body: SubmitReadingAttemptRequest): Promise<SubmitReadingAttemptData> // POST /reading/attempts
```

- **List:** use `getLevelLessons('N5')` and list each lesson's `readingPassages` (`PracticeRef`: `id`, `title`, `xpReward`). The unit of practice is now a passage, not a lesson.
- **Load:** `getPassage(ref.id)`.

| UI reads today (`ReadingData`) | Contract (`ReadingPassageRead`) | Note |
|---|---|---|
| `title` | `title` | nullable; fall back to the lesson title |
| `passages[]` (`japanese`, `vietnamese`) | `contentJapanese`, `contentVietnamese` | One text, not a list. If the per-paragraph translation toggle should stay, split both on `\n` and key the toggle by paragraph index. |
| `content`, `difficulty` | — | Use the lesson's `difficulty`. Drop `content`. |
| `questions[].prompt` | `questions[].questionText` | — |
| `options[].text` | `options[].optionText` | — |
| `words` (hover glossary) | — | Not in the contract. Build it from `getLessonVocabulary(lessonId)` for the passage's lesson, keyed by `kanji ?? kana`, holding `kana`, `kanji`, `romaji` and `meaning`. Drop `level` and `type` from the popup. |

- **Submit:** turn the `Record<questionId, optionId>` into `{ passageId, answers: [{ questionId, selectedOptionId }] }`. Keep the short-answer handling (a typed answer that matches gets the single option's id, otherwise `-1`, which the server grades as wrong).
- **Result:** `is_passed` → `passed`, `xp_gained` → `xpEarned`. `score` is already 0–100, so `max_score` becomes a constant 100.
- Delete `ReadingData`, `Question` and `Option` from `types/index.ts`.

## Step 6: Practice (kaiwa)

`features/practice/api.ts`:

```ts
getDialogue(dialogueId: number): Promise<DialogueRead>                                        // GET /speaking/dialogues/{dialogue_id}
ratePronunciation(body: RatePronunciationRequest): Promise<RatePronunciationResponse>         // POST /speaking/pronunciation (not enveloped)
submitDialogueAttempt(body: SubmitDialogueAttemptRequest): Promise<SubmitDialogueAttemptData> // POST /speaking/attempts
```

| Old | New |
|---|---|
| `GET /lessons/speaking?course_id=1` | `getLevelLessons('N5')` → each lesson's `dialogues` (`PracticeRef`) |
| `GET /lessons/{id}/speaking` → `data.dialogues[0]` | `getDialogue(ref.id)` |
| `conversation[]` (`speaker`, `japanese`, `romaji`, `vietnamese`) | `exchanges[]` sorted by `orderIndex` (`speaker`, `jaText`, `jaRomaji`, `enText`) |
| `POST /speaking/evaluate` `{ expected_text, transcript, romaji }` per line | `ratePronunciation({ expectedText, userTranscript, romaji })` → `{ score, feedback, isCorrect }` |
| Results: average of per-line scores, computed on the client | At the end, `submitDialogueAttempt({ dialogueId, turns })`, where `turns` is `[{ exchangeId, transcript }]` for the user's lines. Show the returned `aiScore`, `aiFeedback` and `xpEarned`. |

- **The translation is now English.** `enText` replaces `vietnamese`, so relabel "Vietnamese Meaning" (see gap G5).
- **Keep the transcripts:** store each user line's transcript with its `exchangeId` while practising, so the final submit can send them.
- **"Simulate" button:** `simulateUserSpeech` submits the expected text as the transcript. Now that the server awards XP for it, this is an XP exploit. Show it only in development (`process.env.NODE_ENV !== 'production'`) or remove it.
- `/speaking/kaiwa` (free conversation) has no UI yet and is out of scope.
- Delete `SpeakingLesson`, `Dialogue`, `DialogueTurn` and `Message` from `types/index.ts`. Keep `ChatMessage` only if it becomes a local view type in the component, and move it there.

## Step 7: Writing

`features/writing/api.ts`:

```ts
getKanjiPractice(practiceId: number): Promise<KanjiPracticeRead>               // GET /writing/kanji/{practice_id}
evaluateWriting(body: EvaluateWritingRequest): Promise<EvaluateWritingData>    // POST /writing/evaluations
```

- **List:** `getLevelLessons('N5')` → each lesson's `kanjiPractices`. This replaces the `N5_VOCABULARY` constants.
- **Evaluate:** `evaluateWriting({ kanjiPracticeId, imageBase64: canvas.toDataURL('image/png') })`. The server accepts the data URL as is. The response is `{ attemptId, score, feedback, xpEarned }`, so `xp_awarded` becomes `xpEarned`.
- The target kanji now comes from the server, not the request. The client no longer sends `target_kanji`.
- **Gap G2:** the card shows `kana (meaning)` under the kanji, but `KanjiPracticeRead` only has `kanji`, `title`, `difficulty` and `xpReward`. Show `title` there until the server adds a reading and meaning.
- The pass colour uses `score >= 60`, which mirrors the server's `WRITING_PASS_SCORE`. Keep it as a named constant in the component.

## Step 8: Clean-up

- Remove `getToken` from `lib/api-client.ts`, along with its "Prefer authFetch" comment. Nothing should import it any more.
- Run these and confirm each has no output:
  ```bash
  grep -rn "fetch(" client/src --include=*.ts --include=*.tsx | grep -v "lib/api-client.ts\|features/auth/session.ts"
  grep -rn "getToken\|API_BASE_URL" client/src --include=*.ts --include=*.tsx | grep -v "lib/api-client.ts\|features/auth/session.ts"
  grep -rn "@/types'" client/src --include=*.ts --include=*.tsx
  ```
  The last grep will still list `lib/constants.ts` and `features/curriculum/lesson-view.tsx`. They're kept on purpose, as dead code, until the lesson materials work decides their fate. `types/index.ts` should then only hold the types those two files use.
- Fix the remaining lint problems, then add `npm run lint` to the client job in `.github/workflows/ci.yml`.
- Delete Part 2 of this document.

## Contract gaps (need a server decision)

None of these blocks the port. Each step above says what to do in the meantime.

| # | Gap | Workaround in the port | Suggested fix |
|---|---|---|---|
| G1 | `GET /courses/{id}/lessons` doesn't say what each lesson contains, so screens fetch every lesson's detail (one request per lesson). | `getLevelLessons` uses `Promise.all`. | Add the counts or `PracticeRef` lists to the lesson list response. |
| G2 | `KanjiPracticeRead` has no reading or meaning. | Show `title`. | Add `kana` and `meaning` to the schema. |
| G3 | Reading passages have no glossary (`words`). | Build it from the lesson's vocabulary. | Fine as is, unless passages need words outside their lesson. |
| G4 | The profile has no phone number. | Show the daily goal instead. | None, unless you want it. |
| G5 | Mixed translation languages: reading has `contentVietnamese`, dialogues have `enText`, vocabulary has `exampleTranslation`. | Label each one as what it is. | Pick one learner language and name fields neutrally (`translation`). |
| G6 | `POST /speaking/attempts` re-rates every line with AI, even though each line was already rated during practice. That's two AI calls per line. | Accept it for now. | Let the attempt reuse the per-line ratings, or skip per-line rating. |
| G7 | A short-answer question has exactly one option, the answer, so the client receives the answer text. | Unchanged from today. | Grade typed answers on the server, and don't send the option text. |
| G8 | No lesson-completion endpoint; XP is per practice. | Lesson decks post reviews instead. | Probably intended. Confirm. |

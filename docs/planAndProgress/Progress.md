# PROJECT PROGRESS - LINGUASPHERE

Cap nhat lan cuoi: 2026-06-18, dua tren doc `forAi/Source`, scan DD Excel va doc code trong `server/`, `client/`.

## 1. Tong Quan Tien Do Chung

- Database & Architecture: `In-Progress`
  - `server/app/db/models.py` da co nhieu bang loi: users, roles, courses, lessons, exercises, tests, onboarding_sessions, learning_plans, user_progress, AI, B2B.
  - Can kiem tra lai migration/runtime vi mot so model co dau hieu chua khop code dang goi.
- Detailed Design: `Done`
  - Thu muc DD da co san, tong quan gom OnBoarding, Hoc tap, CheckList.
  - Can doc DD theo tung task, khong suy doan contract tu ten file.
- Backend API: `In-Progress`
  - Auth co ban da co.
  - Onboarding da co `session`, `answers`, `finalize`, wrapper `submit`, `learner-profile`, `confirm-commitment`, `mark-user-onboarded`.
  - Lessons co code mock/stub sai model.
  - NLP tokenizer da mo router va service, co clean fallback `503` neu env chua co `MeCab`/`unidic`.
  - AI/Gamification/SRS co khung.
- Frontend: `In-Progress`
  - Next App Router da co page auth, dashboard, onboarding, reading, vocabulary, writing.
  - Auth client co ban da goi backend.
  - Onboarding page da goi backend that qua `/api/v1/onboarding/submit`, co loading/error state.

## 2. Chi Muc Tai Lieu Da Doc

| Nhom | Noi dung | Trang thai | Ghi chu |
| :--- | :--- | :--- | :--- |
| Rule | `forAi/rule/rule.md` | Done | Quy dinh bat buoc doc DD, dong bo plan/progress, khong tu che payload |
| Prompt | `forAi/rule/promt.md` | Done | Workflow Analyze -> Update Progress -> Plan -> Update Docs -> Execute |
| Plan | `forAi/planAndProgress/plan.md` | Updated | Da cap nhat master plan chi tiet |
| Progress | `forAi/planAndProgress/Progress.md` | Updated | File nay la tracker hien trang |
| Source summary | `luồng hệ thống.md`, `tóm tắt folder Source.md`, `tóm tắt hệ thống .md` | Updated | Da bo sung endpoint index va hien trang code |
| DD Checklist | `API_Detail_Design_Checklist.xlsx` | Scanned | Checklist Auth/Onboarding co endpoint goi y |
| DD API | `DD/**/*.xlsx` | Indexed | 78 file Excel duoc lap chi muc theo module |

## 3. Thong Ke DD

| Folder DD | So file | Noi dung chinh | Ghi chu |
| :--- | :--- | :--- | :--- |
| `CheckList` | 1 | Checklist tong API design | Co sheet Onboarding API checklist |
| `Học tập/CheckList` | 1 | Checklist Grammar API | Phu tro nhom hoc tap |
| `Học tập/Grammar` | 8 | Topic, lesson, guide, example, exercises, options, attempt, progress | Nhieu file method con placeholder |
| `Học tập/Listening` | 8 | Topic, lesson, audio, subtitle, exercises, options, attempt, progress | Nhieu file method con placeholder |
| `Học tập/Reading` | 8 | Topic, lesson, content, vocabulary, exercises, options, attempt, progress | Method/endpoint ro: GET/POST/PUT |
| `Học tập/Speaking` | 9 | Topic, lesson, prompt, sample, criteria, exercises, analyze, attempt, progress | Can doc sau khi lam Kaiwa |
| `Học tập/Vocabulary` | 11 | Topic, lesson, words, meanings, audio, examples, exercises, options, attempt, study session, progress | Nhieu file method con placeholder |
| `Học tập/Writing` | 7 | Topic, lesson, prompt, reference, exercises, attempt, progress | Gan voi Kanji/Writing |
| `OnBoarding` | 23 | Auth, onboarding, learner profile, learning plan, tests, courses/lessons | Nhom uu tien cao |

## 4. Tien Do Chi Tiet Theo Module

| Module | Task ID | API / Tinh nang theo DD | Backend | Frontend | Ghi chu / Loi phat sinh |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Auth | AUTH_01 | `createUserAccount` - `POST /api/v1/auth/register` | `In-Progress` | `In-Progress` | Backend da nhan `full_name`, `phone` va luu vao `users`; frontend signup da gui `full_name/phone`, nhung response shape/account status van can doi chieu DD |
| Auth | AUTH_02 | `authenticateUser` - `POST /api/v1/auth/login` | `In-Progress` | `In-Progress` | Backend tra `access_token`, `token_type`; can kiem tra DD co user/session fields khong |
| Auth | AUTH_03 | `CheckLoginState` - `POST /api/v1/auth/check-login-state` | `Done` | `N/A` | Da code endpoint, doi chieu `Authorization` va body `sessionToken`, query `users.session_token` va tra `loginState/userId/redirectScreen` |
| Auth | AUTH_04 | `CheckUserByEmailOrPhone` - `POST /api/v1/auth/check-user-by-email-or-phone` | `Done` | `In-Progress` | Da code endpoint duplicate-check theo email/phone, bo sung `users.full_name/phone` + migration, frontend signup da goi check truoc khi register |
| Auth | AUTH_05 | `MarkUserLoggedIn` | `Done` | `N/A` | Da bo sung field `session_token`, `is_logged_in`, `last_login_at` tren `users`; login/register hien tu dong cap nhat login state va da co endpoint `POST /api/v1/auth/mark-user-logged-in` |
| Onboarding | ONB_01 | `CreateOnboardingSession` - `POST /api/v1/onboarding/session` | `Done` | `N/A` | Da code endpoint, secure bang JWT, tao `onboarding_sessions`, include router trong `main.py`; DD co field `sessionToken`/`users.session_token` nhung model hien tai chua co nen dang map tam bang Bearer token request |
| Onboarding | ONB_02 | `SaveOnboardingAnswer` - `POST /api/v1/onboarding/answers` | `Done` | `N/A` | Da upsert theo `session_id + question_code`, luu ca `answer_text` va `answer_value` |
| Onboarding | ONB_03 | `LoadOnboardingAnswersBySessionId` - `GET /api/v1/onboarding/answers` | `Done` | `N/A` | Da query theo `sessionId`, check ownership, tra answers da sort moi nhat truoc |
| Onboarding | ONB_04 | `AnalyzeOnboardingData` - `POST /api/v1/onboarding/analyze` | `Todo` | `Todo` | Co the tinh result_level/result_goal tu answers |
| Onboarding | ONB_05 | `UpsertLearnerProfile` - `POST /api/v1/learner-profile/upsert` | `Done` | `N/A` | Da sua model `LearnerProfiles` ve bang rieng khop migration, da code upsert profile va map `targetGoal -> study_goal`, `experience -> study_mode`; `profileId` hien tam map bang `user_id` vi bang khong co cot id rieng |
| Onboarding | ONB_06 | `ConfirmCommitment` - `POST /api/v1/onboarding/confirm-commitment` | `Done` | `N/A` | Da code endpoint xac nhan token va tra `loginState/userId/redirectScreen`; do schema DB chua co `users.session_token` nen van doi chieu bang Bearer token request |
| Onboarding | ONB_07 | `FinalizeOnboardingSession` - `PUT /api/v1/onboarding/session/finalize` | `Done` | `N/A` | Da update `status=completed`, `completed_at`, `result_level`, `result_goal` |
| Onboarding | ONB_08 | `MarkUserOnboarded` - `PUT /api/v1/users/onboarding/complete` | `Done` | `N/A` | Da bo sung field `is_onboarded`, `onboarded_at` tren `users` va code endpoint update trang thai onboarding cuoi cung |
| Onboarding | ONB_FE_01 | Frontend submit onboarding wizard | `N/A` | `Done` | `client/src/app/onboarding/page.tsx` va `client/src/features/auth/components/onboarding.tsx` da goi backend that, co loading/error state; `Skip for now` khong con submit nham du lieu onboarding |
| Onboarding | ONB_BE_Compat | `POST /api/v1/onboarding/submit` wrapper cho ticket hien tai | `Done` | `Done` | Wrapper tao/reuse active session, luu 3 answers (`starting_level`, `goal`, `time`), finalize va tu dong mark user onboarded de khop flow finish setup |
| Learning Plan | PLAN_01 | `CreateLearningPlan` - `POST /api/v1/learning-plans` | `Todo` | `Todo` | Bang `learning_plans` da co |
| Learning Plan | PLAN_02 | `CreateLearningPlanSteps` - `POST /api/v1/learning-plans/steps` | `Todo` | `Todo` | Bang `learning_plan_steps` da co |
| Tests | TST_01 | `GetPlacementTestByType` - `GET /api/v1/tests/placement` | `Todo` | `Todo` | Bang `tests` da co `test_type` |
| Tests | TST_02 | `GetQuestionsByTestId` - `GET /api/v1/tests/questions` | `Todo` | `Todo` | Bang `test_questions` da co |
| Tests | TST_03 | `GetOptionsByQuestionIds` - `POST /api/v1/questions/options` | `Todo` | `Todo` | Bang `test_question_options` da co |
| Tests | TST_04 | `CreateTestAttempt` - `POST /api/v1/tests/attempts` | `Todo` | `Todo` | Bang `test_attempts` da co |
| Tests | TST_05 | `SaveTestAttemptAnswers` - `POST /api/v1/tests/attempts/answers` | `Todo` | `Todo` | Bang `test_attempt_answers` da co |
| Tests | TST_06 | `LoadLatestTestAttemptByUserId` - `GET /api/v1/tests/attempts/latest` | `Todo` | `Todo` | Can filter user_id + latest |
| Courses | CRS_01 | `GetCoursesByLevel` - `GET /api/v1/courses/by-level` | `Todo` | `Todo` | Model `Courses` co level/status |
| Courses | CRS_02 | `GetLessonsByCourseId` - `GET /api/v1/courses/lessons` | `In-Progress` | `Todo` | `lessons.py` hien sai schema va chua theo DD |
| Reading | READ_01 | `getReadingTopicList` - `GET /api/v1/reading/topics` | `Todo` | `Todo` | DD ro endpoint; data co `server/data/json/reading` |
| Reading | READ_02 | `getReadingLessonById` - `GET /api/v1/reading/lessons/{lessonId}` | `Todo` | `Todo` | Can map lessons/content resource |
| Reading | READ_03 | Reading content/vocab/exercises/options/attempt/progress | `Todo` | `Todo` | 8 DD file da co |
| Grammar | GRAM_01 | Grammar topic/lesson/guide/example/exercises/options/attempt/progress | `Todo` | `Todo` | DD method placeholder, can doc sau |
| Listening | LIST_01 | Listening topic/lesson/audio/subtitle/exercises/options/attempt/progress | `Todo` | `Todo` | DD method placeholder, data json co 3 lesson |
| Vocabulary | VOC_01 | Vocabulary topic/lesson/word/meaning/audio/example/exercises/options/attempt/session/progress | `Todo` | `Todo` | DD method placeholder |
| Speaking | SPK_01 | Speaking topic/lesson/prompt/sample/criteria/exercises/analyze/attempt/progress | `Todo` | `Todo` | Gan voi AI Kaiwa |
| Writing | WRI_01 | Writing topic/lesson/prompt/reference/exercises/attempt/progress | `Todo` | `Todo` | Gan voi Kanji/Writing |
| NLP | NLP_01 | `POST /api/v1/nlp/tokenize` via MeCab | `Done` | `N/A` | Da mo router `nlp.py`, code `MeCabService`, them `mecab-python3` + `unidic`, xu ly empty input va fallback/runtime error ro rang; verify tokenization that con phu thuoc env co cai MeCab hay chua |
| AI Kaiwa | AI_01 | Conversation/Audio Services | `In-Progress` | `In-Progress` | Service va components co san; NLP tokenizer da duoc noi router rieng, con AI explain/Kaiwa router day du lam sau |
| Gamification | GAM_01 | XP/Streak/League | `In-Progress` | `Todo` | `gamification_engine.py`, `league.py` co khung; can doi chieu DB |
| SRS | SRS_01 | Spaced repetition | `In-Progress` | `Todo` | Co service/router, can kiem tra model that |
| B2B/Admin | B2B_01 | Business dashboard/report/user management | `Todo` | `In-Progress` | UI admin co, backend admin router chua include |

## 5. Loi / Xung Dot Critical

1. `server/app/api/v1/lessons.py` dung `models.UserVocabulary`, `current_user.current_progress`, `current_user.streak`, nhung `server/app/db/models.py` khong co cac field/model nay.
2. DD `UpsertLearnerProfile` ky vong `data.profileId`, nhung bang `learner_profiles` trong migration chi co PK `user_id`; code dang adapter `profileId = user_id` cho den khi schema DB duoc mo rong.
3. `server/app/main.py` import `from api.v1 import ...`, trong khi cac module khac import theo namespace `app...`; can test runtime de dam bao import path khong loi.
4. `Users` model da co them session/login/onboarding/full_name/phone fields, nhung response auth va account status chi tiet van chua khop hoan toan voi DD.
6. Frontend signup da gui `full_name`, `phone` va goi duplicate-check, nhung contract response/login flow van can doi chieu them de khop DD auth.
7. Tai lieu rule ghi Next.js 15, package thuc te la Next 16.2.6. Khi code frontend phai bám pattern repo hien tai.
8. `npm run type-check` hien chua chay duoc trong env local vi `client` thieu `tsc`/node_modules; chi moi verify backend bang `python3 -m py_compile`.
9. Runtime NLP hien chua du package `MeCab` va `unidic`; endpoint tokenize se tra loi ro rang `503` cho den khi cai dependency that.

## 6. Next Actions Gan Nhat

1. Auth:
   - Doc sau 2 DD `createUserAccount` va `authenticateUser`.
   - Hoan thien response shape/auth account status cho `register/login/check-login-state` theo DD.
   - Ra soat tiep frontend auth client de khop business code/message va redirect flow.

2. Onboarding:
   - Da co `MarkUserOnboarded` va wrapper `submit` tu dong mark onboarded; can chay migration DB that va verify flow register/login -> session -> finalize -> onboarded.
   - Can nhac bo sung `AnalyzeOnboardingData` va doi frontend tu wrapper `/submit` sang flow DD day du (`session` -> `answers` -> `finalize`) khi placement test duoc mo.

3. Courses/Lessons:
   - Doc `GetCoursesByLevel`, `GetLessonsByCourseId`.
   - Refactor `lessons.py` de query `Courses`, `Lessons`, khong dung model khong ton tai.

4. Placement Test:
   - Code test placement/questions/options/attempt theo DD.
   - Noi vao luong onboarding.

5. Sau moi dot code:
   - Cap nhat file nay voi status that.
   - Neu doi contract/source flow, cap nhat 3 file trong `forAi/Source`.

## 7. Cap Nhat Lan Nay

- Da doi chieu DD:
  - `CreateOnboardingSession_API_Detail_Design.xlsx`
  - `SaveOnboardingAnswer_API_Detail_Design.xlsx`
  - `LoadOnboardingAnswersBySessionId_API_Detail_Design.xlsx`
  - `FinalizeOnboardingSession_API_Detail_Design.xlsx`
  - `UpsertLearnerProfile_API_Detail_Design.xlsx`
  - `ConfirmCommitment_API_Detail_Design.xlsx`
  - `CheckUserByEmailOrPhone_API_Detail_Design.xlsx`
- Da code:
  - `server/app/api/v1/auth.py`
  - `server/app/api/v1/users.py`
  - `server/app/api/v1/onboarding.py`
  - `server/app/db/models.py`
  - `server/app/db/schemas.py`
  - `server/app/api/v1/nlp.py`
  - `server/app/services/mecab_service.py`
  - `server/app/main.py`
  - `server/pyproject.toml`
  - `migrations/versions/5a6d1d4f6b8f_add_user_session_and_onboarding_fields.py`
  - `migrations/versions/8baf3f5c2f11_add_user_profile_fields.py`
  - `client/src/lib/auth.ts`
  - `client/src/app/(auth)/signup/page.tsx`
  - `client/src/features/auth/components/auth-pages.tsx`
  - `client/src/features/auth/components/onboarding.tsx`
  - `client/src/app/onboarding/page.tsx`
- Verify:
  - `python3 -m py_compile server/app/api/v1/auth.py server/app/api/v1/users.py server/app/db/models.py migrations/versions/5a6d1d4f6b8f_add_user_session_and_onboarding_fields.py` -> pass
  - `python3 -m py_compile server/app/api/v1/auth.py server/app/db/models.py server/app/db/schemas.py migrations/versions/8baf3f5c2f11_add_user_profile_fields.py` -> pass
  - `python3 -m py_compile server/app/api/v1/onboarding.py server/app/api/v1/nlp.py server/app/services/mecab_service.py server/app/main.py` -> pass
  - `python3 -m py_compile server/app/api/v1/onboarding.py server/app/services/mecab_service.py server/app/api/v1/nlp.py server/app/main.py` -> pass
  - `python3 -m py_compile server/app/api/v1/onboarding.py server/app/db/models.py` -> pass
  - `npm run type-check` trong `client/` -> fail vi env hien tai thieu `tsc`

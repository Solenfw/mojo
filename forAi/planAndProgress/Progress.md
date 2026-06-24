# PROJECT PROGRESS - LINGUASPHERE

Cap nhat lan cuoi: 2026-06-24, dua tren doc `forAi/Source`, `repomix_summary.xml` va doc code trong `server/`, `client/`.

## 1. Tong Quan Tien Do Chung

- Database & Architecture: `In-Progress`
  - Da dong bo them `users.xp/streak/gems/hearts/hearts_last_updated/last_activity_date` de khop `gamification.py`, `users.py`, `gamification_engine.py`.
  - Da bo sung metadata va rang buoc cho `learner_profiles`, `onboarding_answers`.
  - Can chay `alembic upgrade head` o moi truong that de ap migration moi `b7f9c3a1d2e4`.
  - Da dung duoc moi truong test local voi `server/.venv` va `.env` toi thieu de boot app.
- Detailed Design: `Done`
  - Thu muc DD da co san, tong quan gom OnBoarding, Hoc tap, CheckList.
  - Can doc DD theo tung task, khong suy doan contract tu ten file.
- Backend API: `In-Progress`
  - Auth da doi chieu va sua theo DD cho `register`/`login`, frontend auth client da duoc adapter theo response moi.
  - Onboarding da co router/service co ban, can doi chieu them voi DD.
  - Lessons da co them 2 endpoint courses theo DD; van con can doi chieu tiep cac field map tam thoi voi DB.
  - AI/Gamification/SRS co khung.
- Frontend: `In-Progress`
  - Next App Router da co page auth, dashboard, onboarding, reading, vocabulary, writing.
  - Auth client co ban da goi backend.
  - Frontend onboarding da goi flow backend theo huong `session -> answers -> finalize -> mark onboarded`, van chua noi placement/analyze.

## 2. Chi Muc Tai Lieu Da Doc

| Nhom | Noi dung | Trang thai | Ghi chu |
| :--- | :--- | :--- | :--- |
| Rule | `forAi/rule/rule.md` | Done | Quy dinh bat buoc doc DD, dong bo plan/progress, khong tu che payload |
| Prompt | `forAi/rule/promt.md` | Done | Workflow Analyze -> Update Progress -> Plan -> Update Docs -> Execute |
| Plan | `forAi/planAndProgress/plan.md` | Updated | Da cap nhat master plan chi tiet |
| Progress | `forAi/planAndProgress/Progress.md` | Updated | File nay la tracker hien trang |
| Source summary | `luồng hệ thống.md`, `tóm tắt folder Source.md`, `tóm tắt hệ thống .md` | Updated | Da bo sung endpoint index va hien trang code |
| Runtime/Test | `server/pyproject.toml`, `tests/conftest.py`, `tests/test_auth.py`, `.env` | Updated | Da dung local venv, canh chinh dependency test client, bo sung test auth/onboarding/placement DD payload; suite hien pass `18 passed` va frontend `npm run type-check` pass |
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
| Auth | AUTH_01 | `createUserAccount` - `POST /api/v1/auth/register` | `In-Progress` | `In-Progress` | Da sua request/response theo DD (`fullName/email/phone/passwordHash` -> business payload); frontend signup da gui phone bat buoc |
| Auth | AUTH_02 | `authenticateUser` - `POST /api/v1/auth/login` | `In-Progress` | `In-Progress` | Da sua request/response theo DD (`emailOrPhone/passwordHash` -> accessToken/refreshToken); frontend login da adapter response moi |
| Auth | AUTH_03 | `CheckLoginState` - `POST /api/v1/auth/check-login-state` | `In-Progress` | `Todo` | Da co endpoint + schema/test co ban theo DD; hien dang map token session qua `users.session_token`, chua co co che revoke/persistence day du |
| Auth | AUTH_04 | `CheckUserByEmailOrPhone` - `POST /api/v1/auth/check-user-by-email-or-phone` | `In-Progress` | `In-Progress` | Da co endpoint va frontend signup da goi check; response 200/409 da doi chieu DD co ban |
| Auth | AUTH_05 | `MarkUserLoggedIn` | `In-Progress` | `N/A` | Da co endpoint + schema/test co ban; DB da co `is_logged_in/session_token/last_login_at`, nhung chua cover blocked/soft-delete flow |
| Onboarding | ONB_01 | `CreateOnboardingSession` - `POST /api/v1/onboarding/session` | `In-Progress` | `In-Progress` | Router da co, da include, da co smoke test; frontend onboarding da goi endpoint nay |
| Onboarding | ONB_02 | `SaveOnboardingAnswer` - `POST /api/v1/onboarding/answers` | `In-Progress` | `In-Progress` | Da them unique `(session_id, question_code)` va `updated_at`; frontend onboarding da goi cho 3 answer co ban |
| Onboarding | ONB_03 | `LoadOnboardingAnswersBySessionId` - `GET /api/v1/onboarding/answers` | `In-Progress` | `Todo` | Response da uu tien `updated_at` thay vi `created_at`; da co smoke test |
| Onboarding | ONB_04 | `AnalyzeOnboardingData` - `POST /api/v1/onboarding/analyze` | `In-Progress` | `Todo` | Da them endpoint theo DD (`answerList` + `placementAttempt`), validate attempt/score va tra `currentLevel/recommendedLevel/learningStyle/studyIntensity`; rule-engine hien la heuristic local |
| Onboarding | ONB_05 | `UpsertLearnerProfile` - `POST /api/v1/learner-profile/upsert` | `In-Progress` | `Todo` | Da bo sung `created_at/updated_at`; API tra `updatedAt` theo DB |
| Onboarding | ONB_06 | `ConfirmCommitment` - `POST /api/v1/onboarding/confirm-commitment` | `In-Progress` | `Todo` | Endpoint da co, tra `loginState/userId/redirectScreen`, da co smoke test; can doi chieu them voi DD |
| Onboarding | ONB_07 | `FinalizeOnboardingSession` - `PUT /api/v1/onboarding/session/finalize` | `In-Progress` | `In-Progress` | Bang onboarding_sessions co completed_at/result/status; frontend onboarding da goi endpoint nay |
| Onboarding | ONB_08 | `MarkUserOnboarded` - `PUT /api/v1/users/onboarding/complete` | `In-Progress` | `In-Progress` | Endpoint da co, da chuan hoa business payload va smoke test; frontend onboarding da goi endpoint nay |
| Learning Plan | PLAN_01 | `CreateLearningPlan` - `POST /api/v1/learning-plans` | `Todo` | `Todo` | Bang `learning_plans` da co |
| Learning Plan | PLAN_02 | `CreateLearningPlanSteps` - `POST /api/v1/learning-plans/steps` | `Todo` | `Todo` | Bang `learning_plan_steps` da co |
| Tests | TST_01 | `GetPlacementTestByType` - `GET /api/v1/tests/placement` | `In-Progress` | `Todo` | Da them router `placement_tests.py`, response business payload va smoke test co ban |
| Tests | TST_02 | `GetQuestionsByTestId` - `GET /api/v1/tests/questions` | `In-Progress` | `Todo` | Da them endpoint list questions theo `test_id`, sap xep `sort_order/id`, co smoke test |
| Tests | TST_03 | `GetOptionsByQuestionIds` - `POST /api/v1/questions/options` | `In-Progress` | `Todo` | Da them endpoint list options theo `questionIds`, co smoke test |
| Tests | TST_04 | `CreateTestAttempt` - `POST /api/v1/tests/attempts` | `In-Progress` | `Todo` | Da them endpoint tao attempt va rang `userId` theo access token |
| Tests | TST_05 | `SaveTestAttemptAnswers` - `POST /api/v1/tests/attempts/answers` | `In-Progress` | `Todo` | Da them endpoint cham diem co ban tu `correct_answer`, cap nhat `score/levelEstimate/status`, co smoke test |
| Tests | TST_06 | `LoadLatestTestAttemptByUserId` - `GET /api/v1/tests/attempts/latest` | `In-Progress` | `Todo` | Da them endpoint lay attempt moi nhat theo `user_id`, co smoke test |
| Courses | CRS_01 | `GetCoursesByLevel` - `GET /api/v1/courses/by-level` | `In-Progress` | `Todo` | Da them endpoint theo DD; `estimatedDuration` dang map tu tong `lessons.estimated_minutes`, `thumbnailUrl` tam tra `null` do DB chua co cot |
| Courses | CRS_02 | `GetLessonsByCourseId` - `GET /api/v1/courses/lessons` | `In-Progress` | `Todo` | Da them endpoint theo DD; `lessonOrder` dang map theo thu tu `id ASC` vi DB chua co cot order rieng |
| Reading | READ_01 | `getReadingTopicList` - `GET /api/v1/reading/topics` | `Todo` | `Todo` | DD ro endpoint; data co `server/data/json/reading` |
| Reading | READ_02 | `getReadingLessonById` - `GET /api/v1/reading/lessons/{lessonId}` | `Todo` | `Todo` | Can map lessons/content resource |
| Reading | READ_03 | Reading content/vocab/exercises/options/attempt/progress | `Todo` | `Todo` | 8 DD file da co |
| Grammar | GRAM_01 | Grammar topic/lesson/guide/example/exercises/options/attempt/progress | `Todo` | `Todo` | DD method placeholder, can doc sau |
| Listening | LIST_01 | Listening topic/lesson/audio/subtitle/exercises/options/attempt/progress | `Todo` | `Todo` | DD method placeholder, data json co 3 lesson |
| Vocabulary | VOC_01 | Vocabulary topic/lesson/word/meaning/audio/example/exercises/options/attempt/session/progress | `Todo` | `Todo` | DD method placeholder |
| Speaking | SPK_01 | Speaking topic/lesson/prompt/sample/criteria/exercises/analyze/attempt/progress | `Todo` | `Todo` | Gan voi AI Kaiwa |
| Writing | WRI_01 | Writing topic/lesson/prompt/reference/exercises/attempt/progress | `Todo` | `Todo` | Gan voi Kanji/Writing |
| AI Kaiwa | AI_01 | Conversation/Audio Services | `In-Progress` | `In-Progress` | Service va components co san, router chua noi chinh |
| Gamification | GAM_01 | XP/Streak/League | `In-Progress` | `Todo` | `gamification_engine.py`, `league.py` co khung; can doi chieu DB |
| SRS | SRS_01 | Spaced repetition | `In-Progress` | `Todo` | Co service/router, can kiem tra model that |
| B2B/Admin | B2B_01 | Business dashboard/report/user management | `Todo` | `In-Progress` | UI admin co, backend admin router chua include |
| Database | DB_01 | Dong bo schema/model cho user gamification va onboarding metadata | `Done` | `N/A` | Them migration `b7f9c3a1d2e4_sync_user_gamification_and_onboarding_metadata.py` |
| Test Env | TST_ENV_01 | Dung moi truong test backend local | `Done` | `N/A` | Da bootstrap `pip`, tao `server/.venv`, cai deps, bo sung `.env`, sua stack `starlette/httpx`, va chay pass `pytest` |

## 5. Loi / Xung Dot Critical

1. `server/app/api/v1/lessons.py` da duoc refactor cho `/courses/by-level` va `/courses/lessons`; tuy nhien DB hien chua co `thumbnailUrl` cho course va `lessonOrder` rieng cho lesson, nen backend dang map tam tu du lieu san co.
2. `server/app/api/v1/onboarding.py` khong con trong; da co cac endpoint session/answers/finalize/submit/upsert/confirm, tuy nhien business contract van can doi chieu tiep voi DD.
3. `server/app/main.py` da include onboarding router; dong thoi da bo import `league` khong ton tai de app boot/test duoc.
4. Import style dang tron `server.app...` va `app...`; `python3 -m compileall server/app migrations` va `pytest` dang pass, nhung van nen chuan hoa sau.
5. `Users` model da bo sung field auth/onboarding/gamification can thiet; can ap migration o moi truong that.
6. `LearnerProfiles` hien la bang rieng FK `user_id`, da bo sung timestamp; can tiep tuc doi chieu payload DD.
7. DD Auth goi truong la `passwordHash`, nhung frontend hien van thu plain password tu form; backend dang adapter tam bang cach tu hash neu dau vao khong phai bcrypt/argon2 hash.
8. `object.txt` khong ton tai trong workspace hien tai, nen chua the doi chieu them yeu cau tu file nay.
9. DD cua 2 API Courses/Lessons mo ta `sessionToken` trong body cho `GET`; backend hien ho tro body nay de bam DD, nhung can xac nhan lai voi frontend vi day la pattern khong pho bien.
10. Moi truong test da duoc tao bo sung sau do: `server/.venv` hoat dong va suite auth/onboarding/placement/backend hien dang pass `18 passed`.
13. `server/app/api/v1/onboarding.py` da doi import ve `app.db.schemas` de dong nhat voi cac router khac.
14. Da bo sung `tests/test_onboarding.py` de khoa lai cac flow co ban: create session, save/load answers, finalize session, confirm commitment, mark user onboarded.
15. Da bo sung router placement test `server/app/api/v1/placement_tests.py` va include vao `main.py`; hien moi map phan scored choice co ban dua tren `test_questions.correct_answer`.
16. Da doc DD `AnalyzeOnboardingData_API_Detail_Design.xlsx` va bo sung endpoint `/api/v1/onboarding/analyze` theo contract request/response trong tai lieu.
17. Frontend onboarding orchestration da duoc tach rieng sang `client/src/lib/onboarding.ts`; `auth.ts` quay lai giu pham vi auth/session helper, de mo rong placement/analyze sau nay de hon.
18. Frontend `npm run type-check` da pass sau khi chuan hoa parser loi va tach helper onboarding.
11. Auth DD con nhac `user.status`, `is_deleted`, blocked/soft-delete flow va refresh-token persistence; DB hien tai chua co cac cot/bang nay nen backend moi map duoc nhom success + duplicate/not-found/unauthorized co ban.
12. `CheckLoginState`, `CheckUserByEmailOrPhone`, `MarkUserLoggedIn` da duoc bo sung schema response ro rang hon va co test co ban; tai lieu cu ghi `Todo` nay da khong con dung.

## 6. Next Actions Gan Nhat

1. Ap migration va test backend:
   - Chay `alembic upgrade head`.
   - Tao smoke test tiep cho auth/onboarding/gamification sau khi DB duoc nang cap.

2. Auth:
   - Chot tiep cac nhanh `locked/disabled/soft-delete` neu quyet dinh bo sung schema DB.
   - Ra soat tiep `CheckLoginState`, `CheckUserByEmailOrPhone`, `MarkUserLoggedIn` voi file DD de quyet dinh co can them bang/cot luu refresh-token, revoke state hay khong.
   - Test lai auth sau moi dot sua; hien auth tests dang pass.

3. Onboarding:
   - Doc `CreateOnboardingSession`, `SaveOnboardingAnswer`, `LoadOnboardingAnswersBySessionId`, `FinalizeOnboardingSession`.
   - Doi chieu business code/message/field name voi DD.
   - Noi UI onboarding goi API.

4. Courses/Lessons:
   - Xac nhan mapping tam cho `thumbnailUrl`, `estimatedDuration`, `lessonOrder`, `isPreviewAvailable`.
   - Neu can chinh xac hon, bo sung schema DB/migration cho metadata course/lesson.

5. Placement Test:
   - Code test placement/questions/options/attempt theo DD.
   - Noi vao luong onboarding.

6. Sau moi dot code:
   - Cap nhat file nay voi status that.
   - Neu doi contract/source flow, cap nhat 3 file trong `forAi/Source`.

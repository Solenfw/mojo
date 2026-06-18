# MASTER PLAN - LINGUASPHERE

Cap nhat theo hien trang repo ngay 2026-06-18.

## Tong Quan

LinguaSphere la he thong hoc tieng Nhat tich hop AI, dung FastAPI backend, SQLAlchemy/PostgreSQL, Alembic va Next.js App Router frontend. Moi thay doi code phai doi chieu tai lieu thiet ke trong `forAi/Source/DD-20260618T124646Z-3-001/DD`, dac biet la cac file `*_API_Detail_Design.xlsx`.

Muc tieu gan nhat la dua cac luong Auth, Onboarding, Placement Test va Learning API ve dung contract DD, sau do noi frontend tieu thu API that thay vi UI mock.

## Kien Truc & Ky Thuat

### Backend

- Source chinh: `server/app`.
- Entry point: `server/app/main.py`.
- Dependency/auth: `server/app/api/deps.py`, `server/app/core/security.py`.
- Model DB: `server/app/db/models.py`.
- Schema Pydantic hien tai: `server/app/db/schemas.py`.
- Router hien co: `auth.py`, `users.py`, `srs.py`, `gamification.py`, `lessons.py`, `league.py`, `onboarding.py`, `nlp.py`.
- Router can kich hoat/them moi: cac router learning theo skill neu can tach module.

### Frontend

- Source chinh: `client/src`.
- App Router: `client/src/app`.
- Auth API client hien tai: `client/src/lib/auth.ts`.
- UI auth/onboarding hien tai: `client/src/features/auth/components`.
- Next package trong repo hien la `next@16.2.6`; tai lieu cu ghi Next.js 15. Khi code, uu tien pattern dang co trong repo.

### Tai Lieu DD Bat Buoc Doi Chieu

- Auth/Onboarding: `DD/OnBoarding/*.xlsx`.
- Learning Reading: `DD/Hoc tap/Reading/*.xlsx` (folder thuc te ten `Học tập`).
- Learning Grammar/Listening/Speaking/Vocabulary/Writing: cac folder con trong `DD/Học tập`.
- Checklist tong: `DD/CheckList/API_Detail_Design_Checklist.xlsx`.

## Bảng Tiến Độ Chi Tiết

| Task ID | Hang muc chi tiet | Frontend/Backend | Trang thai | File Source/Tai lieu lien quan | Ghi chu/Loi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| DOC_01 | Lap chi muc toan bo file `.md` trong `forAi` | Docs | Done | `forAi/**/*.md` | Co 7 file md can giu dong bo |
| DOC_02 | Lap chi muc DD theo module | Docs | Done | `forAi/Source/DD-20260618T124646Z-3-001/DD` | Tong 78 file Excel: OnBoarding 23, Hoc tap 52, CheckList 1, checklist phu 2 |
| DOC_03 | Ghi nhan hien trang code backend/frontend | Docs | Done | `server/app`, `client/src` | Da xac dinh onboarding trong, lessons loi schema, auth moi co ban |
| AUTH_01 | Doi chieu createUserAccount DD | Backend | Todo | `DD/OnBoarding/createUserAccount_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py`, `server/app/db/schemas.py` | Can doc sheet Request/Response truoc khi code |
| AUTH_02 | Doi chieu authenticateUser DD | Backend | Todo | `DD/OnBoarding/authenticateUser_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py` | Hien response dang la token co ban, chua chac khop DD |
| AUTH_03 | Cap nhat frontend auth client/form | Frontend | In-Progress | `client/src/lib/auth.ts`, `client/src/features/auth/components/auth-pages.tsx`, `client/src/app/(auth)/signup/page.tsx` | Da gui `full_name/phone`, van can doi chieu them response/login redirect theo DD |
| ONB_01 | CreateOnboardingSession API | Backend | Done | `DD/OnBoarding/CreateOnboardingSession_API_Detail_Design.xlsx`, `server/app/api/v1/onboarding.py` | Da code endpoint va include router; con mismatch nho voi `users.session_token` trong DD |
| ONB_02 | Save/Load Onboarding Answers | Backend | Done | `SaveOnboardingAnswer`, `LoadOnboardingAnswersBySessionId`, `models.OnboardingAnswers` | Da upsert/load answers theo `session_id`, `question_code`, `answer_text`, `answer_value` |
| ONB_03 | UpsertLearnerProfile | Backend | Done | `UpsertLearnerProfile_API_Detail_Design.xlsx`, `models.LearnerProfiles` | Da sua model `LearnerProfiles` khop migration va code endpoint upsert; `profileId` dang adapter bang `user_id` vi schema chua co id rieng |
| ONB_04 | FinalizeOnboardingSession + MarkUserOnboarded | Backend | Done | `FinalizeOnboardingSession`, `MarkUserOnboarded`, `models.OnboardingSessions`, `models.Users` | Da bo sung field onboarding tren `users`, code xong endpoint mark onboarded va migration |
| ONB_06 | ConfirmCommitment API | Backend | Done | `ConfirmCommitment_API_Detail_Design.xlsx`, `server/app/api/v1/onboarding.py` | Da code endpoint; hien da co `users.session_token` trong model/migration de tien sat DD hon |
| ONB_05 | Frontend onboarding submit flow | Frontend | Done | `client/src/app/onboarding/page.tsx`, `client/src/features/auth/components/onboarding.tsx`, `client/src/lib/auth.ts` | Da goi backend that, co loading/error state |
| AUTH_04 | Check login state + mark logged in | Backend | Done | `CheckLoginState_API_Detail_Design.xlsx`, `MarkUserLoggedIn_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py` | Da code endpoint va dong bo login/register cap nhat session/login state |
| AUTH_05 | Check user by email/phone | Backend/Frontend | Done | `CheckUserByEmailOrPhone_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py`, `server/app/db/schemas.py`, `client/src/lib/auth.ts`, `client/src/app/(auth)/signup/page.tsx` | Da code duplicate-check theo email/phone truoc register, bo sung `users.full_name/phone` + migration |
| NLP_01 | Japanese Tokenizer API via MeCab | Backend | Done | `server/app/api/v1/nlp.py`, `server/app/services/mecab_service.py`, `server/pyproject.toml` | Router/service da mo, co fallback `503` neu env chua co MeCab/UniDic; code scope ticket da xong |
| TEST_01 | Placement Test APIs | Backend | Todo | `GetPlacementTestByType`, `GetQuestionsByTestId`, `GetOptionsByQuestionIds` | Bang `tests`, `test_questions`, `test_question_options` da co |
| TEST_02 | Test Attempt APIs | Backend | Todo | `CreateTestAttempt`, `SaveTestAttemptAnswers`, `LoadLatestTestAttemptByUserId` | Bang `test_attempts`, `test_attempt_answers` da co |
| LRN_01 | GetCoursesByLevel | Backend | Todo | `GetCoursesByLevel_API_Detail_Design.xlsx`, `models.Courses` | Endpoint DD: `GET /api/v1/courses/by-level` |
| LRN_02 | GetLessonsByCourseId | Backend | In-Progress | `GetLessonsByCourseId_API_Detail_Design.xlsx`, `server/app/api/v1/lessons.py`, `models.Lessons` | `lessons.py` hien co code mock sai schema |
| LRN_03 | Reading API group | Backend/Frontend | Todo | `DD/Học tập/Reading/*.xlsx`, `server/data/json/reading` | DD Reading co method/endpoint ro nhat trong nhom Hoc tap |
| LRN_04 | Grammar/Listening/Speaking/Vocabulary/Writing API groups | Backend/Frontend | Todo | `DD/Học tập/*/*.xlsx`, `server/data/json/*` | Nhieu DD con de placeholder method `<GET/POST/PUT/DELETE>`, phai doc sau tung sheet |
| AI_01 | Kaiwa/Gemini service router | Backend/Frontend | In-Progress | `server/app/services/gpt_service.py`, `audio_service.py`, `client/src/features/conversation` | Da co service/component khung, chua noi router chinh day du |
| DOC_SYNC | Dong bo Progress sau moi lan code | Docs | Ongoing | `forAi/planAndProgress/Progress.md` | Bat buoc cap nhat sau khi sua code lon |

## Ke Hoach Tiep Theo

1. Chot Auth theo DD:
   - Doc `createUserAccount_API_Detail_Design.xlsx` va `authenticateUser_API_Detail_Design.xlsx`.
   - Chot tiep response schema/business code trong `server/app/db/schemas.py`.
   - Sua tiep `server/app/api/v1/auth.py` cho register/login/check-login-state neu DD can them account status.
   - Ra soat `client/src/lib/auth.ts` va form signup/login de khop response/redirect that.
   - Chay backend tests hoac it nhat import/compile check.

2. Hoan thien Onboarding con thieu:
   - Bo sung `AnalyzeOnboardingData` neu muon tach logic tong hop khoi `finalize`.
   - Ra quyet dinh ve viec co can them `id` rieng cho `learner_profiles` hay tiep tuc adapter `profileId=user_id`.
   - Can nhac doi frontend onboarding sang flow DD day du thay cho wrapper `/submit` sau khi placement test xong. Hien ticket backend/frontend submit wizard da xong va `submit` da tu dong mark onboarded.

3. Sua Learning Courses/Lessons:
   - Doc `GetCoursesByLevel_API_Detail_Design.xlsx`.
   - Doc `GetLessonsByCourseId_API_Detail_Design.xlsx`.
   - Refactor `server/app/api/v1/lessons.py` de bo `UserVocabulary`, `current_progress`, `streak`.
   - Dung model that `Courses`, `Lessons`, `UserProgress` neu can progress.

4. Trien khai Placement Test:
   - Doc cac DD Tests trong `OnBoarding`.
   - Code endpoints query `Tests`, `TestQuestions`, `TestQuestionOptions`.
   - Code attempt luu cau tra loi vao `TestAttempts`, `TestAttemptAnswers`.

5. Day NLP qua muc runnable:
   - Cai `MeCab` va `unidic` trong env backend.
   - Chay test thu `POST /api/v1/nlp/tokenize` voi chuoi Nhat that.
   - Neu can, mo rong response/token parsing theo format UniDic trong env thuc te.

## Nguyen Tac Thuc Thi

- Truoc khi code mot API, phai mo dung file DD tuong ung va doc sheet `OverView`, `Resquest`, `Response`, `Data Processing Flow`, `Error`.
- Khong tu them field vao request/response neu DD da chot contract.
- Neu DD va model hien tai mau thuan, ghi ro vao `Progress.md` va de xuat huong: sua model/migration hay adapter response.
- Neu thay doi schema DB, phai tao/kiem tra Alembic migration.
- Neu sua frontend tieu thu API, phai doi chieu endpoint backend that va env `NEXT_PUBLIC_API_URL`.

# MASTER PLAN - LINGUASPHERE

Cap nhat theo hien trang repo ngay 2026-06-24.

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
- Router hien co: `auth.py`, `users.py`, `srs.py`, `gamification.py`, `lessons.py`, `onboarding.py`, `nlp.py`, `speaking.py`, `writing.py`.
- Router/thanh phan con thieu hoac can tach moi: `league.py` (hien chua ton tai trong repo), cac router learning theo skill neu can tach module.
- Moi truong test local da tao duoc qua `server/.venv`; can duy tri dependency stack tuong thich `fastapi + starlette<1.0 + httpx`.

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
| DOC_03 | Ghi nhan hien trang code backend/frontend | Docs | Done | `server/app`, `client/src` | Da xac dinh lessons loi schema, auth moi co ban, onboarding da co khung can doi chieu DD |
| AUTH_01 | Doi chieu createUserAccount DD | Backend | In-Progress | `DD/OnBoarding/createUserAccount_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py`, `server/app/db/schemas.py` | Da sua request/response theo DD; con can quyet dinh xu ly passwordHash/client hashing va account status DB |
| AUTH_02 | Doi chieu authenticateUser DD | Backend | In-Progress | `DD/OnBoarding/authenticateUser_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py` | Da sua request/response theo DD; con thieu nhanh locked/soft-delete vi DB chua co cot |
| AUTH_03 | Cap nhat frontend auth client/form | Frontend | In-Progress | `client/src/lib/auth.ts`, `client/src/features/auth/components/auth-pages.tsx` | Da adapter login/register, check-user va bat dau noi onboarding flow backend; con can doi chieu tiep placement/analyze fullstack |
| AUTH_04 | Hoan thien `CheckLoginState` / `CheckUserByEmailOrPhone` / `MarkUserLoggedIn` | Backend | In-Progress | `DD/OnBoarding/CheckLoginState_API_Detail_Design.xlsx`, `CheckUserByEmailOrPhone_API_Detail_Design.xlsx`, `MarkUserLoggedIn_API_Detail_Design.xlsx`, `server/app/api/v1/auth.py` | Da co endpoint, da bo sung response schema/test co ban; con thieu blocked/soft-delete/revoke state theo DD mo rong |
| ONB_01 | CreateOnboardingSession API | Backend | In-Progress | `DD/OnBoarding/CreateOnboardingSession_API_Detail_Design.xlsx`, `server/app/api/v1/onboarding.py` | Router da co va da include; can doi chieu them business contract DD |
| ONB_02 | Save/Load Onboarding Answers | Backend | In-Progress | `SaveOnboardingAnswer`, `LoadOnboardingAnswersBySessionId`, `models.OnboardingAnswers` | Da them unique/index + `updated_at`; con can doi chieu field/response theo DD |
| ONB_03 | UpsertLearnerProfile | Backend | In-Progress | `UpsertLearnerProfile_API_Detail_Design.xlsx`, `models.LearnerProfiles` | Da bo sung timestamp cho learner profile, con can doi chieu them contract DD |
| ONB_04 | FinalizeOnboardingSession + MarkUserOnboarded | Backend | In-Progress | `FinalizeOnboardingSession`, `MarkUserOnboarded`, `models.OnboardingSessions` | Da co field onboarded trong model; can ap migration va doi chieu contract DD |
| ONB_05 | AnalyzeOnboardingData API | Backend | In-Progress | `AnalyzeOnboardingData_API_Detail_Design.xlsx`, `server/app/api/v1/onboarding.py` | Da them endpoint theo DD va smoke test; rule-engine hien la heuristic local, chua co service rieng/audit log |
| TEST_01 | Placement Test APIs | Backend | In-Progress | `GetPlacementTestByType`, `GetQuestionsByTestId`, `GetOptionsByQuestionIds`, `server/app/api/v1/placement_tests.py` | Da them router va response schema/test co ban; can doi chieu them voi DD chi tiet |
| TEST_02 | Test Attempt APIs | Backend | In-Progress | `CreateTestAttempt`, `SaveTestAttemptAnswers`, `LoadLatestTestAttemptByUserId`, `server/app/api/v1/placement_tests.py` | Da them router va score/level estimate co ban; can xac nhan tiep cach cham diem theo DD |
| LRN_01 | GetCoursesByLevel | Backend | In-Progress | `GetCoursesByLevel_API_Detail_Design.xlsx`, `models.Courses` | Da code endpoint; `thumbnailUrl`/duration dang map tam theo DB hien co |
| LRN_02 | GetLessonsByCourseId | Backend | In-Progress | `GetLessonsByCourseId_API_Detail_Design.xlsx`, `server/app/api/v1/lessons.py`, `models.Lessons` | Da code endpoint; `lessonOrder` dang suy ra theo `id ASC` do DB chua co cot rieng |
| LRN_03 | Reading API group | Backend/Frontend | Todo | `DD/Học tập/Reading/*.xlsx`, `server/data/json/reading` | DD Reading co method/endpoint ro nhat trong nhom Hoc tap |
| LRN_04 | Grammar/Listening/Speaking/Vocabulary/Writing API groups | Backend/Frontend | Todo | `DD/Học tập/*/*.xlsx`, `server/data/json/*` | Nhieu DD con de placeholder method `<GET/POST/PUT/DELETE>`, phai doc sau tung sheet |
| AI_01 | Kaiwa/Gemini service router | Backend/Frontend | In-Progress | `server/app/services/gpt_service.py`, `audio_service.py`, `client/src/features/conversation` | Da co service/component khung, chua noi router chinh day du |
| DB_01 | Dong bo users/gamification va metadata onboarding | Backend/DB | Done | `server/app/db/models.py`, `migrations/versions/b7f9c3a1d2e4_sync_user_gamification_and_onboarding_metadata.py` | Them `xp/streak/gems/hearts`, timestamp profile, unique/index cho onboarding answers |
| TST_ENV_01 | Dung moi truong test backend local + sua test stack | Backend/Docs | Done | `server/.venv`, `server/pyproject.toml`, `tests/conftest.py`, `tests/test_auth.py`, `tests/test_onboarding.py`, `.env` | Da bootstrap pip/virtualenv, chinh `starlette/httpx`, va chay pass `pytest` |
| DOC_SYNC | Dong bo Progress sau moi lan code | Docs | Ongoing | `forAi/planAndProgress/Progress.md` | Da cap nhat lai ngay 2026-06-24 sau dot sua schema/database |

## Ke Hoach Tiep Theo

1. Chot Auth theo DD:
   - Doc `createUserAccount_API_Detail_Design.xlsx` va `authenticateUser_API_Detail_Design.xlsx`.
   - Tiep tuc chot `CheckLoginState`, `CheckUserByEmailOrPhone`, `MarkUserLoggedIn` o cac nhanh loi/trang thai nang cao.
   - Quyet dinh co can them schema DB cho `status`, `is_deleted`, refresh-token persistence hay khong.
   - Sua `client/src/lib/auth.ts` va form signup/login neu payload/flow con thay doi.
   - Chay lai backend tests sau moi dot sua.

2. Hoan tat Onboarding API nen tang:
   - Doc `CreateOnboardingSession`, `SaveOnboardingAnswer`, `LoadOnboardingAnswersBySessionId`, `FinalizeOnboardingSession`.
   - Tiep tuc doi chieu contract DD cho response/business code.
   - Include router trong `server/app/main.py`.
   - Schema Pydantic request/response da co; tiep tuc chinh field neu DD khac.
   - Cap nhat `Progress.md`.
   - Tach rule-engine/analysis service cho `AnalyzeOnboardingData` neu can mo rong them audit log va recommendation logic.

3. Sua Learning Courses/Lessons:
   - Doc `GetCoursesByLevel_API_Detail_Design.xlsx`.
   - Doc `GetLessonsByCourseId_API_Detail_Design.xlsx`.
   - Xac nhan va chot mapping cho `thumbnailUrl`, `estimatedDuration`, `lessonOrder`, `isPreviewAvailable`.
   - Dung model that `Courses`, `Lessons`, `UserProgress` neu can progress.

4. Trien khai Placement Test:
   - Doc cac DD Tests trong `OnBoarding`.
   - Ra soat va chot contract cua router `placement_tests.py` voi DD.
   - Xac nhan tiep cach cham diem/cap `levelEstimate` va co can tranh duplicate answer cho 1 attempt hay khong.

5. Noi frontend onboarding:
   - `client/src/lib/onboarding.ts` da goi `session -> answers -> finalize -> mark onboarded`, con thieu placement/analyze.
   - Tiep tuc giu `auth.ts` gon, neu mo rong onboarding thi uu tien bo sung trong `client/src/lib/onboarding.ts`.
   - Dam bao token duoc gui qua `Authorization: Bearer <token>`.

## Nguyen Tac Thuc Thi

- Truoc khi code mot API, phai mo dung file DD tuong ung va doc sheet `OverView`, `Resquest`, `Response`, `Data Processing Flow`, `Error`.
- Khong tu them field vao request/response neu DD da chot contract.
- Neu DD va model hien tai mau thuan, ghi ro vao `Progress.md` va de xuat huong: sua model/migration hay adapter response.
- Neu thay doi schema DB, phai tao/kiem tra Alembic migration.
- Neu sua frontend tieu thu API, phai doi chieu endpoint backend that va env `NEXT_PUBLIC_API_URL`.
- Neu tai lieu tham chieu khong ton tai trong repo (vd `object.txt`), phai ghi nhan ro trong `Progress.md` thay vi suy doan noi dung.

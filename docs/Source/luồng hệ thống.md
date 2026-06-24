# LUONG HE THONG - LINGUASPHERE

Cap nhat: 2026-06-18.

Tai lieu nay tom tat luong nghiep vu va diem gan code can bám khi trien khai. Nguon chuan gom Use Case, Activity Diagram va DD Excel trong `forAi/Source/DD-20260618T124646Z-3-001/DD`.

## 1. Luong Xac Thuc

### Muc tieu

Nguoi dung tao tai khoan, dang nhap, giu phien va truy cap cac API can Bearer token.

### API DD lien quan

| API | Endpoint theo DD | Auth | Trang thai code |
| :--- | :--- | :--- | :--- |
| `createUserAccount` | `POST /api/v1/auth/register` | None | Da co backend co ban, chua khop day du DD |
| `authenticateUser` | `POST /api/v1/auth/login` | Bearer JWT trong DD | Da co backend co ban |
| `CheckLoginState` | `POST /api/v1/auth/check-login-state` | Bearer Session Token | Da co backend; query theo `users.session_token` va tra `redirectScreen` |
| `CheckUserByEmailOrPhone` | `POST /api/v1/auth/check-user-by-email-or-phone` | None | Da co backend va dang duoc frontend signup goi truoc register |
| `MarkUserLoggedIn` | `POST /api/v1/auth/mark-user-logged-in` | Bearer Access Token | Da co backend; login/register cung tu dong cap nhat login state |

### Code hien tai

- Backend: `server/app/api/v1/auth.py`.
- Schema: `server/app/db/schemas.py`.
- Auth dependency: `server/app/api/deps.py`.
- Frontend API client: `client/src/lib/auth.ts`.
- UI: `client/src/features/auth/components/auth-pages.tsx`.

### Rủi ro

- `Users` model da co session/login/onboarding/full_name/phone fields, nhung response auth va account status van can doi chieu them theo DD.
- Frontend signup da gui `full_name`, `phone` kem `username` fallback; can tiep tuc chot response/redirect flow.
- Can doc DD truoc khi quyet dinh bo sung them field/business code auth.

## 2. Luong Onboarding & Ca Nhan Hoa

### Muc tieu

Sau khi dang nhap, nguoi dung tao onboarding session, tra loi cau hoi muc tieu/trinh do, lam placement test, tao learner profile, cam ket lich hoc va hoan tat onboarding.

### API DD lien quan

| API | Endpoint theo DD | DB/Table gan nhat | Trang thai code |
| :--- | :--- | :--- | :--- |
| `CreateOnboardingSession` | `POST /api/v1/onboarding/session` | `onboarding_sessions` | Da co |
| `SaveOnboardingAnswer` | `POST /api/v1/onboarding/answers` | `onboarding_answers` | Da co |
| `LoadOnboardingAnswersBySessionId` | `GET /api/v1/onboarding/answers` | `onboarding_answers` | Da co |
| `AnalyzeOnboardingData` | `POST /api/v1/onboarding/analyze` | `onboarding_sessions`, `learner_profiles` | Chua co |
| `UpsertLearnerProfile` | `POST /api/v1/learner-profile/upsert` | `learner_profiles` | Da co backend; `profileId` dang adapter bang `user_id` |
| `ConfirmCommitment` | `POST /api/v1/onboarding/confirm-commitment` | `learner_profiles` | Da co backend |
| `FinalizeOnboardingSession` | `PUT /api/v1/onboarding/session/finalize` | `onboarding_sessions` | Da co |
| `MarkUserOnboarded` | `PUT /api/v1/users/onboarding/complete` | `users` | Da co backend; can migrate DB that |

### Code hien tai

- `server/app/api/v1/onboarding.py` da co session/answers/finalize/submit, learner profile, confirm commitment.
- `server/app/main.py` da include onboarding router.
- `client/src/features/auth/components/onboarding.tsx` da goi backend that qua wrapper submit; `Skip for now` chi redirect, khong submit du lieu mac dinh.
- Wrapper `POST /api/v1/onboarding/submit` hien cung tu dong mark user la da onboarded sau khi finalize.

## 3. Luong Placement Test & Kiem Tra

### Muc tieu

He thong lay bai test dau vao theo loai, lay cau hoi, lay options, tao attempt, luu cau tra loi va nap attempt gan nhat de suy ra trinh do.

### API DD lien quan

| API | Endpoint theo DD | DB/Table |
| :--- | :--- | :--- |
| `GetPlacementTestByType` | `GET /api/v1/tests/placement` | `tests` |
| `GetQuestionsByTestId` | `GET /api/v1/tests/questions` | `test_questions` |
| `GetOptionsByQuestionIds` | `POST /api/v1/questions/options` | `test_question_options` |
| `CreateTestAttempt` | `POST /api/v1/tests/attempts` | `test_attempts` |
| `SaveTestAttemptAnswers` | `POST /api/v1/tests/attempts/answers` | `test_attempt_answers` |
| `LoadLatestTestAttemptByUserId` | `GET /api/v1/tests/attempts/latest` | `test_attempts` |

### Ghi chu

- Nen trien khai sau Auth/Onboarding session de co current user/token on dinh.
- Can doc DD de xac dinh query param/body exact cho `testType`, `testId`, `questionIds`, `attemptId`.

## 4. Luong Learning Core

Nguoi dung hoc theo 6 ky nang: Grammar, Vocabulary, Reading, Listening, Writing/Kanji, Speaking/AI Kaiwa.

### Courses/Lessons

| API | Endpoint theo DD | Trang thai code |
| :--- | :--- | :--- |
| `GetCoursesByLevel` | `GET /api/v1/courses/by-level` | Chua co endpoint dung DD |
| `GetLessonsByCourseId` | `GET /api/v1/courses/lessons` | `lessons.py` co code cu sai schema |

Bang lien quan: `courses`, `lessons`, `lesson_resources`, `exercises`, `exercise_options`, `exercise_attempts`, `user_progress`.

### Reading

DD Reading co endpoint/method ro:

- `GET /api/v1/reading/topics`
- `GET /api/v1/reading/lessons/{lessonId}`
- `GET /api/v1/reading/lessons/{lessonId}/content-resource`
- `GET /api/v1/reading/lessons/{lessonId}/vocabulary-resource`
- `POST /api/v1/reading/exercise-options/by-ids`
- `GET /api/v1/reading/lessons/{lessonId}/exercises`
- `POST /api/v1/reading/attempts`
- `PUT /api/v1/reading/progress`

Dữ liệu nguồn: `server/data/json/reading`, ban dau copy/tuong ung voi `forAi/Source/json_nihon/reading_json`.

### Grammar/Listening/Speaking/Vocabulary/Writing

Cac nhom nay da co DD, nhung nhieu file con de method placeholder `<GET/POST/PUT/DELETE>` trong sheet OverView. Khi trien khai bat buoc doc ky sheet `Resquest` va `Data Processing Flow` cua tung file.

## 5. Luong AI Kaiwa

### Muc tieu

Nguoi dung hoi thoai bang text/audio voi AI, nhan phan tich phat am/ngu phap, luu lich su va phan hoi.

### Code hien tai

- Services: `server/app/services/gpt_service.py`, `audio_service.py`, `tts_service.py`, `mecab_service.py`.
- Frontend: `client/src/features/conversation/components/kaiwa-practice.tsx`, `live-call.tsx`.
- Router NLP da duoc include trong `server/app/main.py`; tokenizer co fallback ro rang neu env thieu `MeCab`/`UniDic`.

### Bang lien quan

- `ai_conversations`
- `ai_messages`
- `tutor_sessions`
- `tutor_session_feedback`
- `user_weaknesses`

## 6. Luong Theo Doi, SRS, Gamification

### Muc tieu

Luu tien do hoc, diem XP, streak/league, yeu diem va nhac on tap theo spaced repetition.

### Code hien tai

- `server/app/api/v1/srs.py`
- `server/app/services/srs_engine.py`
- `server/app/api/v1/gamification.py`
- `server/app/services/gamification_engine.py`
- `server/app/api/v1/league.py`

### Rủi ro

- Can kiem tra cac service co dang goi field/model cu khong.
- `lessons.py` da xac nhan co goi field/model khong ton tai.

## 7. Luong B2B/Admin/VIP

### B2B/Admin

Use Case co actor `Business_B2B`, `Admin`, cac chuc nang quan ly hoc vien, xem bao cao, quan ly content/user/AI.

Bang lien quan:

- `business_orgs`
- `business_members`
- `business_student_assignments`
- `reports`
- `admin_actions`

Code hien tai:

- Frontend admin co `client/src/features/admin/components/admin-dashboard.tsx`.
- Backend `admin.py` ton tai nhung router chua include trong `main.py`.

### VIP/WebRTC

Use Case co hoc voi nguoi ban xu qua WebRTC. Frontend co `dashboard/live`, `live-call.tsx`; backend can tiep tuc thiet ke session/tutor API khi co DD hoac yeu cau rieng.

## 8. Thu Tu Uu Tien Trien Khai

1. Auth theo DD con thieu alignment sau cung cho payload/response register-login-account-state.
2. Onboarding con thieu `AnalyzeOnboardingData` va frontend flow DD day du.
3. Placement test va test attempt.
4. Courses/Lessons theo DD, dong thoi sua `lessons.py`.
5. Reading API group vi DD ro nhat.
6. Cac nhom learning con lai.
7. AI Kaiwa, SRS, Gamification dong bo DB.
8. Admin/B2B/VIP.

# TOM TAT FOLDER SOURCE - LINGUASPHERE

Cap nhat: 2026-06-18.

Thu muc `forAi/Source` la nguon tai lieu thiet ke chinh de AI va developer doi chieu truoc khi code. Tuyet doi khong bo qua DD Excel neu task lien quan den API da duoc thiet ke.

## 1. Cau Truc Tong Quan

```text
forAi/Source/
├── luồng hệ thống.md
├── tóm tắt folder Source.md
├── tóm tắt hệ thống .md
├── Biểu đồ Activity-20260618T125115Z-3-001/
├── Biểu đồ UC(Chức năng tổng quát)-20260618T125116Z-3-001/
├── DD-20260618T124646Z-3-001/
│   └── DD/
│       ├── CheckList/
│       ├── Học tập/
│       └── OnBoarding/
└── json_nihon/
    ├── Kanji_json/
    ├── Listening_json/
    └── reading_json/
```

## 2. Tai Lieu Use Case

Folder:

`Biểu đồ UC(Chức năng tổng quát)-20260618T125116Z-3-001/Biểu đồ UC(Chức năng tổng quát)/Phân tích thiết kế hệ thống`

Noi dung chinh:

- Actors: `User_B2C`, `Business_B2B`, `Admin`, `AI`.
- Nhom chuc nang:
  - Onboarding & Ca nhan hoa.
  - Hoc tap: tu vung, doc, nghe, noi AI Kaiwa, viet Kanji, ngu phap.
  - Kiem tra & danh gia.
  - Theo doi & ho tro.
  - VIP/nang cao.
  - Doanh nghiep.
  - Admin.
- Cac nang luc AI:
  - Sua phat am thoi gian thuc.
  - ChatBot giai dap.
  - Goi y bai hoc ca nhan hoa.
  - Dua ra diem yeu.
  - Bao cao hang tuan/thang.

## 3. Tai Lieu Activity Diagram

Folder:

`Biểu đồ Activity-20260618T125115Z-3-001/Biểu đồ Activity`

File chinh:

| File | Noi dung |
| :--- | :--- |
| `Onboarding & Cá nhân hóa, Admin.drawio` | Luong onboarding, ca nhan hoa, admin lien quan |
| `Biểu đồ hoạt động học tập.drawio` | Luong hoc Grammar/Listening/Reading... |
| `Biểu đồ hoạt động kiểm tra&đánh giá (1).drawio` | Luong test, cham diem, luu ket qua |
| `Theo_doi_va_ho_tro.drawio` | Theo doi tien do, chatbot, nhac nho, email |
| `Chức năng VIP.drawio` | Hoc voi nguoi ban xu/WebRTC |
| `Biểu đồ hd  doanh nghiệp.drawio` | B2B dashboard, hoc vien, bao cao |

Mot so buoc Activity da scan:

- Hoc Grammar: chon chu de, lay cau hoi/dap an, hien huong dan/vi du, lam bai, kiem tra dap an, luu ket qua, cap nhat tien do.
- Listening: chon chu de, lay audio/phu de/cau hoi, phat audio, tra loi, kiem tra, luu ket qua, cap nhat tien do.
- B2B: dang nhap, dashboard quan tri, truy xuat DB, xem/xuat bao cao, quan ly hoc vien.

## 4. Detailed Design API

Folder goc:

`forAi/Source/DD-20260618T124646Z-3-001/DD`

### Thong ke

| Nhom | So file | Ghi chu |
| :--- | :--- | :--- |
| `CheckList` | 1 | Checklist tong API DD |
| `Học tập/CheckList` | 1 | Checklist Grammar |
| `Học tập/Grammar` | 8 | Grammar APIs |
| `Học tập/Listening` | 8 | Listening APIs |
| `Học tập/Reading` | 8 | Reading APIs |
| `Học tập/Speaking` | 9 | Speaking/Kaiwa APIs |
| `Học tập/Vocabulary` | 11 | Vocabulary APIs |
| `Học tập/Writing` | 7 | Writing APIs |
| `OnBoarding` | 23 | Auth, onboarding, tests, courses, learning plan |

Tong file Excel DD/API checklist da scan: 78.

### Format Excel Pho Bien

Moi file `*_API_Detail_Design.xlsx` thuong co cac sheet:

- `OverView`
- `Resquest` (ten sheet trong file bi viet sai chinh ta, nhung can dung dung ten khi doc)
- `Response`
- `Data Processing Flow`
- `Error`

Khi code API:

1. Doc `OverView` de lay API name, endpoint, method, auth, timeout.
2. Doc `Resquest` de lay header/path/query/body exact.
3. Doc `Response` de lay status code, business code, output fields.
4. Doc `Data Processing Flow` de biet validate, DB table, transaction.
5. Doc `Error` de map HTTPException/business error.

## 5. Chi Muc API OnBoarding

| API | Endpoint | Method |
| :--- | :--- | :--- |
| `AnalyzeOnboardingData` | `/api/v1/onboarding/analyze` | POST |
| `authenticateUser` | `/api/v1/auth/login` | POST |
| `CheckLoginState` | `/api/v1/auth/check-login-state` | POST |
| `CheckUserByEmailOrPhone` | `/api/v1/auth/check-user-by-email-or-phone` | POST |
| `ConfirmCommitment` | `/api/v1/onboarding/confirm-commitment` | POST |
| `CreateLearningPlan` | `/api/v1/learning-plans` | POST |
| `CreateLearningPlanSteps` | `/api/v1/learning-plans/steps` | POST |
| `CreateOnboardingSession` | `/api/v1/onboarding/session` | POST |
| `CreateTestAttempt` | `/api/v1/tests/attempts` | POST |
| `createUserAccount` | `/api/v1/auth/register` | POST |
| `FinalizeOnboardingSession` | `/api/v1/onboarding/session/finalize` | PUT |
| `GetCoursesByLevel` | `/api/v1/courses/by-level` | GET |
| `GetLessonsByCourseId` | `/api/v1/courses/lessons` | GET |
| `GetOptionsByQuestionIds` | `/api/v1/questions/options` | POST |
| `GetPlacementTestByType` | `/api/v1/tests/placement` | GET |
| `GetQuestionsByTestId` | `/api/v1/tests/questions` | GET |
| `LoadLatestTestAttemptByUserId` | `/api/v1/tests/attempts/latest` | GET |
| `LoadOnboardingAnswersBySessionId` | `/api/v1/onboarding/answers` | GET |
| `MarkUserLoggedIn` | `/api/v1/auth/mark-user-logged-in` | POST |
| `MarkUserOnboarded` | `/api/v1/users/onboarding/complete` | PUT |
| `SaveOnboardingAnswer` | `/api/v1/onboarding/answers` | POST |
| `SaveTestAttemptAnswers` | `/api/v1/tests/attempts/answers` | POST |
| `UpsertLearnerProfile` | `/api/v1/learner-profile/upsert` | POST |

Ghi chu hien trang code:

- Da co backend cho `CreateOnboardingSession`, `SaveOnboardingAnswer`, `LoadOnboardingAnswersBySessionId`, `FinalizeOnboardingSession`, `UpsertLearnerProfile`, `ConfirmCommitment`, `MarkUserOnboarded`.
- Wrapper `POST /api/v1/onboarding/submit` cung da tu dong finalize session va mark user onboarded cho flow frontend hien tai.
- Da co backend cho `CheckLoginState`, `MarkUserLoggedIn`, `CheckUserByEmailOrPhone`.
- Con thieu `AnalyzeOnboardingData` va alignment day du auth payload/response theo DD.

## 6. Chi Muc API Reading

| API | Endpoint | Method |
| :--- | :--- | :--- |
| `getReadingTopicList` | `/api/v1/reading/topics` | GET |
| `getReadingLessonById` | `/api/v1/reading/lessons/{lessonId}` | GET |
| `getReadingContentResourceByLessonId` | `/api/v1/reading/lessons/{lessonId}/content-resource` | GET |
| `getReadingVocabularyResourceByLessonId` | `/api/v1/reading/lessons/{lessonId}/vocabulary-resource` | GET |
| `getReadingExerciseOptionsByExerciseIds` | `/api/v1/reading/exercise-options/by-ids` | POST |
| `getReadingExercisesByLessonId` | `/api/v1/reading/lessons/{lessonId}/exercises` | GET |
| `saveReadingAttempt` | `/api/v1/reading/attempts` | POST |
| `updateReadingProgress` | `/api/v1/reading/progress` | PUT |

## 7. Chi Muc Learning Con Lai

Nhieu file DD trong Grammar/Listening/Speaking/Vocabulary/Writing co endpoint goi y nhung method trong OverView con de placeholder `<GET/POST/PUT/DELETE>`. Khi thuc hien task cac module nay, bat buoc doc sau tung file.

Vi du endpoint goi y:

- Grammar: `/api/v1/grammar/topics`, `/api/v1/grammar/lessons/{lessonId}`, `/api/v1/grammar/exercises/{lessonId}`, `/api/v1/grammar/attempts`, `/api/v1/grammar/progress`.
- Listening: `/api/v1/listening/topics`, `/api/v1/listening/lessons/{lessonId}`, `/api/v1/listening/audio/{lessonId}`, `/api/v1/listening/subtitle/{lessonId}`.
- Speaking: `/api/v1/speaking/topics`, `/api/v1/speaking/lessons/{lessonId}`, `/api/v1/speaking/analyze`.
- Vocabulary: `/api/v1/vocabulary/topics`, `/api/v1/vocabulary/lessons/{lessonId}`, `/api/v1/vocabulary/words/{lessonId}`, `/api/v1/vocabulary/study-session`.
- Writing: `/api/v1/writing/topics`, `/api/v1/writing/lessons/{lessonId}`, `/api/v1/writing/prompts/{lessonId}`, `/api/v1/writing/attempts`.

## 8. Du Lieu JSON Nihon

Folder:

`forAi/Source/json_nihon`

| Folder | File | Cau truc top-level |
| :--- | :--- | :--- |
| `Kanji_json` | `kanji_b2.json` | `lesson`, `grammar_points`, `kanji_vocabulary`, `practice` |
| `Kanji_json` | `kanji_lesson_1_fixed.json` | `lesson`, `grammar_points`, `dialogues` |
| `Kanji_json` | `kanji_lesson_3.json`, `kanji_lesson_4.json` | `lesson`, `grammar_points`, `kanji_vocabulary`, `practice_exercises` |
| `Listening_json` | `listening_lesson_1..3.json` | `lesson`, `source_file`, `listening_passages` |
| `reading_json` | `reading_lesson_1..6.json` | `lesson`, `title`, `reading_passages`, `vocabulary`, `exercises` |

Repo server hien co ban copy/bo sung tai:

- `server/data/json/grammar`
- `server/data/json/kanji`
- `server/data/json/listening`
- `server/data/json/reading`
- `server/data/json/speaking`
- `server/data/json/vocabulary`

## 9. Cach Dung Folder Source Khi Code

1. Xac dinh module va API can lam.
2. Mo dung file DD trong `DD`.
3. Neu lien quan luong nguoi dung, doc them drawio/activity tuong ung.
4. Doi chieu model trong `server/app/db/models.py`.
5. Doi chieu router/schema hien co.
6. Code backend/frontend.
7. Cap nhat `forAi/planAndProgress/Progress.md`.
8. Neu contract/flow thay doi lon, cap nhat lai cac file Source summary.

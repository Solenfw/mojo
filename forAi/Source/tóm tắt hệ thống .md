# TOM TAT HE THONG - LINGUASPHERE

Cap nhat: 2026-06-18.

## 1. Thong Tin Chung

- Ten du an: LinguaSphere.
- Muc tieu: Nen tang hoc tieng Nhat tich hop AI, uu tien nguoi di lam va muc tieu JLPT N5/N4 nen tang.
- Kien truc: Monorepo backend FastAPI + frontend Next.js.
- Nguon thiet ke: Use Case, Activity Diagram, API Detailed Design Excel trong `forAi/Source`.

## 2. Actor

| Actor | Vai tro |
| :--- | :--- |
| `User_B2C` | Hoc vien ca nhan: onboarding, hoc tap, lam test, theo doi tien do, hoi thoai AI |
| `Business_B2B` | Doanh nghiep: quan ly hoc vien, xem/xuat bao cao |
| `Admin` | Quan tri user, content, AI/system |
| `AI` | Chatbot, goi y bai hoc, phan tich diem yeu, sua phat am/ngu phap, bao cao |

## 3. Tech Stack

### Backend

- FastAPI.
- Python 3.12+.
- SQLAlchemy ORM.
- Alembic migrations.
- PostgreSQL.
- JWT auth qua `python-jose`.
- Pydantic v2.
- AI/NLP services: Gemini, MeCab, TTS/STT service khung.

### Frontend

- Next.js App Router.
- React 19.
- Tailwind CSS v4.
- TypeScript.
- Motion, lucide-react, Recharts.
- Package thuc te trong `client/package.json`: `next@16.2.6`.

### Data

- PostgreSQL cho user/progress/test/content metadata.
- JSON lesson data trong `server/data/json` va source goc `forAi/Source/json_nihon`.
- Excel DD la contract API chinh.

## 4. Module He Thong

### Auth

Chuc nang:

- Dang ky.
- Dang nhap.
- Kiem tra trang thai dang nhap.
- Kiem tra user bang email/phone.
- Cap nhat trang thai logged-in.

Code hien tai:

- Backend: `server/app/api/v1/auth.py`.
- Frontend: `client/src/lib/auth.ts`, `client/src/features/auth/components/auth-pages.tsx`.

Trang thai:

- Co register/login co ban.
- Chua dong bo day du voi DD.
- Can xu ly mismatch `fullName`/`username`, email/phone, login state.

### Onboarding & Ca Nhan Hoa

Chuc nang:

- Tao onboarding session.
- Luu cau tra loi onboarding.
- Phan tich du lieu onboarding.
- Upsert learner profile.
- Cam ket thoi gian hoc.
- Hoan tat onboarding.

Code hien tai:

- Backend: `server/app/api/v1/onboarding.py` da co flow onboarding co ban va learner profile.
- Frontend: `client/src/features/auth/components/onboarding.tsx` co UI; `client/src/lib/onboarding.ts` da bat dau goi onboarding API that cho flow co ban.

Trang thai:

- Chua trien khai API.
- La nhom uu tien cao sau Auth.

### Placement Test & Assessment

Chuc nang:

- Lay placement test theo type.
- Lay questions/options.
- Tao test attempt.
- Luu cau tra loi.
- Lay attempt gan nhat.
- Luu ket qua/level estimate.

DB da co:

- `tests`
- `test_questions`
- `test_question_options`
- `test_attempts`
- `test_attempt_answers`

Trang thai:

- Chua co router/API day du.

### Learning Core

Chuc nang:

- Lay courses theo level.
- Lay lessons theo course.
- Hoc 6 ky nang: Grammar, Vocabulary, Reading, Listening, Writing/Kanji, Speaking.
- Lay topic, lesson, resource, exercises, options.
- Luu attempt va update progress.

DB da co:

- `courses`
- `lessons`
- `lesson_resources`
- `exercises`
- `exercise_options`
- `exercise_attempts`
- `user_progress`

Trang thai:

- `server/app/api/v1/lessons.py` dang co code cu sai schema.
- Reading DD ro nhat va nen lam som sau Courses/Lessons.
- Cac nhom learning con lai can doc DD sau do quyet method/contract.

### AI Kaiwa

Chuc nang:

- Hoi thoai AI bang text/audio.
- Phan tich cau noi, phat am, ngu phap.
- Luu hoi thoai.
- Goi y/sua loi.

Code hien tai:

- Backend services co khung: `gpt_service.py`, `audio_service.py`, `tts_service.py`, `mecab_service.py`.
- Frontend co component conversation/live call.

Trang thai:

- Chua noi API router chinh day du.

### SRS & Gamification

Chuc nang:

- On tap ngat quang.
- XP, streak, league.
- Cap nhat tien do sau attempt/lesson.

Code hien tai:

- `server/app/api/v1/srs.py`
- `server/app/services/srs_engine.py`
- `server/app/api/v1/gamification.py`
- `server/app/services/gamification_engine.py`
- `server/app/api/v1/league.py` (tai lieu cu co nhac, nhung file hien chua ton tai trong repo)

Trang thai:

- Co khung.
- Can audit field/model truoc khi goi tu lesson completion.

### B2B/Admin/VIP

Chuc nang:

- B2B quan ly hoc vien va bao cao.
- Admin quan ly user/content/AI.
- VIP hoc voi nguoi ban xu qua WebRTC.

DB da co:

- `business_orgs`
- `business_members`
- `business_student_assignments`
- `reports`
- `admin_actions`
- `tutor_sessions`
- `tutor_session_feedback`

Trang thai:

- Frontend admin/live co khung.
- Backend router admin/social/shop co file nhung nhieu router chua include.

## 5. Hien Trang Codebase

### Backend

| File | Trang thai |
| :--- | :--- |
| `server/app/main.py` | Include auth/users/srs/gamification/lessons/onboarding/nlp/speaking/writing; `league` khong ton tai nen da bo import |
| `server/app/db/models.py` | Model DB day du nhung can audit vai class/field mismatch |
| `server/app/db/schemas.py` | Moi co schema auth co ban |
| `server/app/api/v1/auth.py` | Register/login/token co ban |
| `server/app/api/v1/onboarding.py` | Trong |
| `server/app/api/v1/lessons.py` | Co code cu sai model |

### Frontend

| File/Folder | Trang thai |
| :--- | :--- |
| `client/src/app` | App Router pages da co |
| `client/src/lib/auth.ts` | Auth fetch client co ban |
| `client/src/features/auth/components` | Login/signup/onboarding UI co san |
| `client/src/features/conversation` | Kaiwa/live UI co san |
| `client/src/features/lesson`, `reading`, `vocab`, `kanji` | Learning UI co khung |

## 6. Critical Gaps

1. Auth chua khop DD va co mismatch frontend/backend payload.
2. Onboarding API chua co.
3. Courses/Lessons API chua theo DD; `lessons.py` dung field/model khong ton tai.
4. Placement Test API chua co.
5. Pydantic schema moi rat mong, chua phu cac response DD.
6. Mot so DD Learning con placeholder method, can doc sau truoc khi code.
7. Frontend van chua tieu thu day du onboarding/test/learning API that, nhung onboarding co ban da noi `session/answers/finalize/mark onboarded`.

## 7. Uu Tien Phat Trien

1. Auth DD alignment.
2. Onboarding API.
3. Placement Test API.
4. Courses/Lessons API.
5. Reading API group.
6. Noi frontend onboarding.
7. Learning skill APIs con lai.
8. AI Kaiwa/SRS/Gamification integration.
9. Admin/B2B/VIP.

## 8. Quy Tac Dong Bo Tai Lieu

- Sau moi task code, cap nhat `forAi/planAndProgress/Progress.md`.
- Neu thay doi ke hoach, cap nhat `forAi/planAndProgress/plan.md`.
- Neu thay doi luong he thong/API contract/schema lon, cap nhat:
  - `forAi/Source/luồng hệ thống.md`
  - `forAi/Source/tóm tắt folder Source.md`
  - `forAi/Source/tóm tắt hệ thống .md`

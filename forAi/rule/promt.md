# PROMPT VAN HANH - UPDATE PROGRESS, PLAN & CODE

Cap nhat: 2026-06-18.

Dung prompt nay khi nguoi dung yeu cau phan tich, cap nhat tien do, lap plan hoac code trong du an LinguaSphere.

## 1. Ngu Canh Du An

- Du an: LinguaSphere.
- Backend: `server/` - FastAPI, SQLAlchemy, Alembic, PostgreSQL.
- Frontend: `client/` - Next.js App Router, React, Tailwind, TypeScript.
- Tai lieu thiet ke: `forAi/Source/`.
- DD API: `forAi/Source/DD-20260618T124646Z-3-001/DD`.
- Plan/progress: `forAi/planAndProgress/`.
- Rule bat buoc: `forAi/rule/rule.md`.

## 2. Khi Nhan Yeu Cau Moi

Thuc hien theo thu tu:

### Buoc 1: Phan Tich Yeu Cau

Xac dinh:

- Module lien quan.
- Co DD API hay khong.
- Can backend, frontend hay fullstack.
- Co can doi DB/migration khong.
- Co can cap nhat tai lieu khong.

Neu yeu cau co lien quan API da co DD, tim file Excel tuong ung trong:

`forAi/Source/DD-20260618T124646Z-3-001/DD`

### Buoc 2: Doc DD

Doc cac sheet:

- `OverView`: API name, endpoint, method, auth, summary.
- `Resquest`: headers, path/query/body, required fields, constraints, sample payload.
- `Response`: status, business code, response fields, sample.
- `Data Processing Flow`: validation, DB access, transaction, service logic.
- `Error`: error code, HTTP status, cause, handling.

Khong duoc suy doan payload neu DD co noi dung.

### Buoc 3: Doc Code Hien Tai

Backend:

- `server/app/main.py`
- `server/app/api/deps.py`
- `server/app/db/models.py`
- `server/app/db/schemas.py`
- `server/app/api/v1/<module>.py`
- `server/app/services` neu co business logic.

Frontend:

- `client/src/lib`
- `client/src/app`
- `client/src/features`
- `client/src/types`

### Buoc 4: Cap Nhat Progress Truoc/Trong Khi Lam

Neu phat hien trang thai trong `Progress.md` sai voi code, cap nhat lai.

File:

`forAi/planAndProgress/Progress.md`

Ghi ro:

- Task ID.
- Trang thai moi.
- File DD da doc.
- File code lien quan.
- Loi/xung dot neu co.

### Buoc 5: Lap Ke Hoach Thuc Thi

Neu task lon, ghi plan ngan trong phan trao doi hoac cap nhat `plan.md`.

Plan can neu:

- File se sua.
- Schema/API se them.
- Logic DB.
- Frontend integration.
- Test/check se chay.

### Buoc 6: Code

Chi code sau khi da co du context.

Nguyen tac:

- Sua nho, bám pattern hien co.
- Dung schema ro.
- Dung model DB that.
- Khong them abstraction neu khong can.
- Khong refactor lan man.
- Khong revert thay doi cua nguoi dung.

### Buoc 7: Verify

Tuy task, chay mot hoac nhieu lenh:

- Backend import/compile check.
- Pytest neu co test.
- Frontend type-check/build neu sua frontend.
- Manual API shape check neu can.

Neu khong chay duoc test, ghi ro ly do.

### Buoc 8: Cap Nhat Tai Lieu Sau Khi Code

Cap nhat:

- `Progress.md`: trang thai that sau code.
- `plan.md`: neu doi priority/next actions.
- 3 file Source summary: neu doi flow/schema/API contract lon.

## 3. Module Priority Hien Tai

1. Auth:
   - `createUserAccount`
   - `authenticateUser`
   - `CheckLoginState`
   - `CheckUserByEmailOrPhone`

2. Onboarding:
   - `CreateOnboardingSession`
   - `SaveOnboardingAnswer`
   - `LoadOnboardingAnswersBySessionId`
   - `UpsertLearnerProfile`
   - `ConfirmCommitment`
   - `FinalizeOnboardingSession`

3. Placement Test:
   - `GetPlacementTestByType`
   - `GetQuestionsByTestId`
   - `GetOptionsByQuestionIds`
   - `CreateTestAttempt`
   - `SaveTestAttemptAnswers`
   - `LoadLatestTestAttemptByUserId`

4. Courses/Lessons:
   - `GetCoursesByLevel`
   - `GetLessonsByCourseId`
   - Refactor `server/app/api/v1/lessons.py`

5. Learning APIs:
   - Reading first, vi DD ro method/endpoint nhat.
   - Sau do Grammar, Listening, Vocabulary, Speaking, Writing.

## 4. Hien Trang Can Kiem Tra Truoc Khi Code

- `.gitignore` dang co thay doi san trong worktree; khong dung neu khong lien quan.
- `onboarding.py` trong.
- `main.py` chua include onboarding router.
- `lessons.py` co code sai model.
- `schemas.py` moi co auth schema co ban.
- Frontend onboarding chua goi API.
- Frontend signup `fullName` co the khong khop backend `username`.

## 5. Mau Bao Cao Sau Khi Lam

Khi ket thuc task, tra loi ngan gon:

- Da sua nhung file nao.
- Logic chinh da them/sua.
- DD nao da doi chieu.
- Test/check da chay va ket qua.
- Viec con lai/rui ro neu co.

Vi du:

```text
Da cap nhat Auth theo DD createUserAccount/authenticateUser:
- Sua schema request/response trong ...
- Sua endpoint ...
- Sua frontend client ...
Check: pytest ... pass.
Progress.md da cap nhat AUTH_01/AUTH_02.
```

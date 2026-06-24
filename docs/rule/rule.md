# AI INSTRUCTIONS - LINGUASPHERE

Cap nhat: 2026-06-18.

Tai lieu nay la rule bat buoc cho AI/developer khi lam viec trong du an LinguaSphere.

## 1. Vai Tro & Muc Tieu

AI dong vai tro:

- Technical Project Manager.
- Fullstack Solutions Architect.
- Backend/FastAPI engineer.
- Frontend/Next.js engineer.
- Documentation maintainer cho folder `forAi`.

Muc tieu:

- Code dung yeu cau nguoi dung.
- Bám sat thiet ke goc trong `forAi/Source`.
- Dong bo tien do trong `forAi/planAndProgress`.
- Khong pha vo contract API da co trong DD.

## 2. Tech Stack Chuan

### Backend

- FastAPI.
- Python 3.12+.
- SQLAlchemy.
- Alembic.
- PostgreSQL.
- Pydantic v2.
- JWT auth.

Thu muc chinh:

- `server/app/main.py`
- `server/app/api`
- `server/app/api/v1`
- `server/app/db/models.py`
- `server/app/db/schemas.py`
- `server/app/services`

### Frontend

- Next.js App Router.
- React 19.
- Tailwind CSS v4.
- TypeScript.

Thu muc chinh:

- `client/src/app`
- `client/src/features`
- `client/src/components`
- `client/src/lib`
- `client/src/types`

Ghi chu: Tai lieu cu co the ghi Next.js 15, nhung package hien tai trong repo la Next 16.2.6. Khi code phai uu tien pattern thuc te trong repo.

## 3. Nguon Su That Theo Thu Tu Uu Tien

Khi co mau thuan, uu tien theo thu tu:

1. Yeu cau moi nhat cua nguoi dung.
2. File DD Excel tuong ung trong `forAi/Source/DD-20260618T124646Z-3-001/DD`.
3. Use Case va Activity Diagram trong `forAi/Source`.
4. Code hien tai trong `server/` va `client/`.
5. `forAi/planAndProgress`.
6. Suy luan cua AI.

Neu DD va code hien tai mau thuan, khong tu y quyet dinh im lang. Phai ghi ro trong progress hoac bao cho user neu can chon huong.

## 4. Quy Trinh Bat Buoc Truoc Khi Code

### Buoc 1: Xac dinh module

Phan loai yeu cau vao mot hoac nhieu module:

- Auth.
- Onboarding.
- Placement Test.
- Courses/Lessons.
- Reading.
- Grammar.
- Listening.
- Vocabulary.
- Speaking/AI Kaiwa.
- Writing/Kanji.
- SRS/Gamification.
- Admin/B2B/VIP.

### Buoc 2: Doc tai lieu DD

Neu API da co DD, bat buoc mo file Excel tuong ung.

Folder DD:

`forAi/Source/DD-20260618T124646Z-3-001/DD`

Sheet can doc:

- `OverView`
- `Resquest`
- `Response`
- `Data Processing Flow`
- `Error`

Luu y:

- Ten sheet `Resquest` trong file bi viet sai chinh ta; van phai doc dung sheet nay.
- Khong chi doc ten file.
- Khong chi doc endpoint trong checklist.
- Nhieu file Learning de method placeholder `<GET/POST/PUT/DELETE>`, phai doc sau sheet Request/Flow truoc khi code.

### Buoc 3: Doc code hien tai

Toi thieu phai kiem tra:

- Model DB trong `server/app/db/models.py`.
- Pydantic schema trong `server/app/db/schemas.py`.
- Router lien quan trong `server/app/api/v1`.
- Dependency/auth trong `server/app/api/deps.py`.
- Frontend API client trong `client/src/lib`.
- Frontend UI trong `client/src/app` va `client/src/features`.

### Buoc 4: Doi chieu va lap plan ngan

Truoc khi sua file, xac dinh:

- File DD nao dang bám.
- Request payload chuan.
- Response payload chuan.
- Bang DB dung.
- File backend se sua.
- File frontend se sua.
- Test/command se chay.
- Tai lieu progress nao can cap nhat.

## 5. Quy Tac Code Backend

- Router API phai dung prefix `/api/v1` khi include trong `main.py`.
- Endpoint/method/path/query/body phai theo DD.
- Pydantic schema phai ro request/response, khong tra dict tuy tien khi DD co schema.
- Query DB dung model thuc te trong `models.py`.
- Khong goi model/field khong ton tai.
- Neu can field DB moi, phai:
  - Ghi ro ly do.
  - Sua model.
  - Tao/kiem tra migration Alembic.
  - Cap nhat tai lieu.
- Auth endpoint can dung `Depends(get_current_user)` hoac dependency phu hop neu DD yeu cau Bearer token.
- Loi validation/auth/not found/conflict phai map theo DD neu DD co Error sheet.

## 6. Quy Tac Code Frontend

- Dung pattern da co trong `client/src`.
- API client nen dat trong `client/src/lib` hoac feature-specific lib neu module lon.
- Gui token qua `Authorization: Bearer <token>` khi DD yeu cau auth.
- Khong hard-code response shape neu backend/DD da co type ro.
- UI phai tieu thu API that khi task yeu cau fullstack, khong de mock neu danh dau Done.
- Neu form field khac DD/backend, phai sua de dong bo.

## 7. Quy Tac Cap Nhat Tai Lieu

### Bat buoc cap nhat `Progress.md` khi:

- Them/sua API.
- Sua schema/model.
- Noi frontend voi backend.
- Phat hien bug/xung dot contract.
- Hoan thanh hoac doi trang thai task.

File:

`forAi/planAndProgress/Progress.md`

### Cap nhat `plan.md` khi:

- Thay doi thu tu uu tien.
- Them module/task lon.
- Tach task moi.
- Co dependency/rui ro moi anh huong ke hoach.

File:

`forAi/planAndProgress/plan.md`

### Cap nhat 3 file Source summary khi:

- Doi luong nghiep vu.
- Doi API contract so voi DD.
- Them/sua bang DB lon.
- Them module moi.

Files:

- `forAi/Source/luồng hệ thống.md`
- `forAi/Source/tóm tắt folder Source.md`
- `forAi/Source/tóm tắt hệ thống .md`

## 8. Format Trang Thai

Dung cac trang thai:

- `Todo`
- `In-Progress`
- `Done`
- `Blocked`
- `N/A`

Khong danh dau `Done` neu:

- Backend chua khop DD.
- Frontend chua tieu thu API trong task fullstack.
- Chua chay duoc test/check toi thieu.
- Con mismatch request/response chua ghi ro.

## 9. Mau Tracker Cho File Plan/Progress

Moi module nen co bang:

| Task ID | Hang muc chi tiet | Frontend/Backend | Trang thai | File Source/Tai lieu lien quan | Ghi chu/Loi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| MOD_01 | Mo ta task | Backend | Todo | DD file + code file | Ghi chu |

## 10. Strict Restrictions

- Cam tu y sang tao API payload/response neu DD da co.
- Cam sua code khi chua doc file DD lien quan, tru cac task khong lien quan API/DD.
- Cam revert thay doi nguoi dung neu khong duoc yeu cau.
- Cam danh dau task Done chi vi code compile, phai bám contract va luong nguoi dung.
- Cam bo qua loi schema/model mismatch; phai ghi lai.
- Cam sua thiet ke lon ma khong cap nhat tai lieu.

## 11. Hien Trang Can Nho

- `server/app/api/v1/onboarding.py` hien trong.
- `server/app/api/v1/lessons.py` dang goi `UserVocabulary`, `current_progress`, `streak` khong ton tai.
- `server/app/main.py` chua include onboarding router.
- Auth backend/frontend co ban nhung chua dong bo day du DD.
- DD OnBoarding va Reading la nhom co endpoint/method ro nhat.
- Mot so DD Learning con placeholder method.

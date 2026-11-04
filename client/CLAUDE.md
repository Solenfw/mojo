# Client

**Layering** (`client/src/`): `app/` holds routes only; `features/<domain>/<name>-view.tsx` holds UI; `features/<domain>/api.ts` has one typed function per endpoint (verb-named: `get*`, `submit*`, `review*`...) that throws `ApiError` on failure. Components never call `fetch`/`api` directly. Features may import another feature's `api.ts` but not its components; `features/curriculum/api.ts` is the shared owner of levels, courses and lessons.

**Not yet on the API:** `src/app/admin`, `src/app/dashboard/live` (mockups), and `src/features/curriculum/lesson-view.tsx` (still reads static data from `lib/constants.ts` and `types/index.ts`; both files go away once it is ported).

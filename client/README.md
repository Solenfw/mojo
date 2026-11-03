# Mojo client

Next.js 16 (App Router) + React 19 + Tailwind CSS v4, managed with npm. Every command runs from this directory; imports are rooted at `src` through the `@/` alias. In day-to-day use, run things through the root `Makefile`, which points the client at the API.

## Layout

```text
client/
├── src/
│   ├── app/                   # routes only: pages and layouts that compose feature views
│   │   ├── (auth)/            # login, signup, forgot-password (shared auth layout)
│   │   ├── onboarding/        # first-run questionnaire, behind AuthGuard
│   │   ├── dashboard/         # the signed-in app, behind AuthGuard (one folder per screen)
│   │   ├── admin/             # admin dashboard
│   │   └── api/webhooks/      # Next.js route handler (stub)
│   ├── features/              # one folder per domain: <name>-view.tsx (UI) + api.ts (calls)
│   │   └── auth/              # session.ts (login/register/logout), auth-guard.tsx
│   ├── components/ui/         # shared primitives (button, card, dialog, tabs, ...)
│   ├── lib/
│   │   ├── api-client.ts      # typed `api` client, `unwrap`, `ApiError`, access-token handling
│   │   └── utils.ts           # cn(): merges Tailwind class names
│   └── types/
│       ├── api.generated.ts   # generated from openapi.json; never edit by hand
│       └── index.ts           # UI-only types for screens not yet on the API
├── docs/api-layer.md          # rules for calling the API; read before adding an endpoint
├── openapi.json               # API contract exported from the server
└── package.json
```

Domains match the server's: `features/reading/api.ts` calls `/api/v1/reading/*`, defined in `server/app/api/v1/reading.py`.

## Conventions

- **Layers.** Pages in `app/` compose views. Views in `features/<name>/` hold UI state and rendering and get their data only from their feature's `api.ts`. `api.ts` calls the typed `api` client. Components never call `fetch` directly. The full rules are in [docs/api-layer.md](docs/api-layer.md).
- **Contract.** Wire types come from `@/types/api.generated` only, and paths, params and bodies are checked against `openapi.json` at compile time. Contract changes start on the server: change the schema, run `make api-types`, commit `openapi.json` and `api.generated.ts`, then run `npm run type-check` to find every broken call site.
- **Auth.** The access token is kept in memory only, never in storage. The refresh token is an httpOnly cookie, which `lib/api-client.ts` uses to restore the session after a page load, refresh it before expiry, and retry once on a 401. `AuthGuard` sends signed-out users to `/login`.
- **Server-owned rules.** Scores, XP and levels are computed by the server. The client shows `xpEarned` and other results as returned and never sends or adds them up itself.
- **Configuration.** The only setting is `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). It is inlined at build time, so a production build has to be made against the API it will talk to.
- **Style.** Prettier (single quotes, 2-space indent, 100 columns) and ESLint with `eslint-config-next`.

## Status

These screens are still UI-only, with no API behind them:

- `admin/` and `dashboard/live/`: mockups with placeholder data.
- `features/curriculum/lesson-view.tsx`: reads static N5 data from `lib/constants.ts` and the types in `types/index.ts`. Move it to `features/curriculum/api.ts`, then remove both files.
- `app/api/webhooks/route.ts`: returns `{ ok: true }`.

## Commands

From the repo root (see `make help`):

```bash
make client-install         # npm install
make client-dev             # dev server on http://localhost:3000, against API_URL
make client-build           # production build, against API_URL
make client-typecheck       # tsc --noEmit
make api-types              # regenerate openapi.json and src/types/api.generated.ts from the server
make client-dev API_URL=https://api.example.com   # point at a different API
```

Directly, from `client/`:

```bash
npm run dev                 # next dev (NEXT_PUBLIC_API_URL defaults to http://localhost:8000)
npm run build && npm start  # production build and server
npm run lint                # eslint
npm run type-check          # tsc --noEmit
npm run gen:api             # regenerate src/types/api.generated.ts from the committed openapi.json
```

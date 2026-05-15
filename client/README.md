# LinguaSphere Client

Next.js frontend for LinguaSphere, an AI-assisted Japanese learning platform.

## Tech Stack

- Next.js 16 App Router
- React 19
- TypeScript
- Tailwind CSS
- Base UI primitives and local UI components
- Lucide React icons
- Motion animations
- Recharts
- Google Gemini client integration
- Bun for dependency management and scripts

## Requirements

- Bun
- Node.js 18.17+ compatible runtime

## Setup

Install dependencies:

```bash
bun install
```

Create local environment values:

```bash
cp .env.example .env.local
```

Set the values needed for your local run:

```env
GEMINI_API_KEY="your-gemini-api-key"
APP_URL="http://localhost:3000"
```

## Development

Start the Next.js dev server:

```bash
bun run dev
```

Open `http://localhost:3000`.

## Scripts

```bash
bun run dev         # Start the development server
bun run build       # Create a production build
bun run start       # Start the production server after build
bun run type-check  # Run TypeScript without emitting files
```

These are the scripts currently defined in `package.json`.

## App Routes

The app uses the Next.js App Router under `src/app`.

```text
src/app/
├── page.tsx                         # Landing page
├── (auth)/
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   └── forgot-password/page.tsx
├── onboarding/page.tsx
├── admin/page.tsx
├── dashboard/
│   ├── page.tsx
│   ├── curriculum/page.tsx
│   ├── vocabulary/page.tsx
│   ├── practice/page.tsx
│   ├── reading/page.tsx
│   ├── writing/page.tsx
│   └── live/page.tsx
└── api/webhooks/route.ts
```

## Source Layout

```text
src/
├── app/          # Next.js routes, layouts, and route handlers
├── components/   # Shared UI and layout components
├── features/     # Feature-specific screens and components
├── hooks/        # Shared React hooks
├── lib/          # Shared utilities and integrations
├── store/        # Client state modules
├── types/        # TypeScript types
└── utils/        # Constants and helper utilities
```

## Notes

- Use Bun commands for frontend work.
- Backend API development happens from the repository root with uv against the `server/` project.
- Keep route files in `src/app` valid Next.js modules; empty route, layout, loading, or error files will break type checking.

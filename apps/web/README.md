# AI Job Match Web

Next.js dashboard for the AI Job Match project.

## Run locally

From the repository root:

```powershell
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000.

The frontend uses `http://localhost:8000` by default. If the API runs elsewhere, create `apps/web/.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Current UI

- Candidate profile setup and resume upload
- Ranked job recommendations
- Server-side search, location, remote, and employment-type filters
- Match score with matched/missing skills and reasons
- Skill-gap priorities
- Curated learning resources
- Save jobs and view saved jobs
- Track applications and change status
- Configurable match-score alerts
- Current alert matches

The alert feature currently evaluates the latest job dataset when the dashboard checks it; email/push notification delivery is intentionally not implemented yet.

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

The frontend expects the FastAPI backend at `http://localhost:8000`. Copy `.env.example` to `.env.local` if the backend runs elsewhere.

## Current UI

- Candidate profile setup
- Resume upload
- Ranked job recommendations
- Search and remote filtering
- Match score and matched/missing skills
- Skill-gap priorities
- Learning resources
- Direct application links when a source provides one

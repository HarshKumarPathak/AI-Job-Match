# AI Job Match

AI-powered job aggregation, recommendation, and skill-gap analysis platform.

## Vision

AI Job Match helps candidates understand **which jobs fit their profile, why they fit, what skills are missing, and what to learn next**.

## Core capabilities

- Resume upload and structured profile extraction
- Job aggregation through pluggable sources
- Job normalization and deduplication
- Hybrid job recommendation
- Explainable match scores
- Skill-gap analysis
- Personalized learning recommendations
- Job search, filters, saved jobs, and applications
- Configurable job alerts

## Architecture

```
Next.js / TypeScript
        |
        v
    FastAPI API
        |
  +-----+------------------+
  |                        |
  v                        v
PostgreSQL + pgvector   NLP/ML services
  |                        |
  +-----------+------------+
              |
        Job source adapters
```

## Project structure

```
apps/
  web/                 # Next.js frontend
services/
  api/                 # FastAPI backend
  worker/              # background jobs
ml/
  resume/              # resume extraction
  matching/            # ranking + recommendation
  skills/              # skill normalization + gap analysis
infra/
  docker/              # local infrastructure
docs/
  architecture/        # design documentation
scripts/               # development utilities
```

## Development status

Phase 1 — core product foundation implemented; semantic embeddings are optional and scheduled ingestion is included. Email alert delivery is implemented as an optional SMTP integration; it stays disabled until SMTP settings are configured. Alert notifications are deduplicated per alert/job.

## Engineering principles

- Source adapters are isolated from recommendation logic.
- Recommendations are explainable, not black-box scores.
- Job data is normalized before ranking.
- External job sources must be used only through permitted APIs, feeds, or public career endpoints.
- Secrets stay out of Git.
- ML components remain replaceable so the baseline can be evaluated against semantic/hybrid approaches.

## Planned stack

- Next.js + TypeScript
- FastAPI + Python
- PostgreSQL (with pgvector-ready infrastructure)
- scikit-learn
- sentence-transformers
- spaCy
- Redis + background workers
- Docker

## License

MIT


## Current API capabilities

The backend currently supports:

- Candidate profile creation
- PDF/DOCX/TXT resume text extraction
- Basic explainable skill extraction and normalization
- Job ingestion with source/external-ID deduplication
- Candidate-to-job match scoring
- Job detail pages with salary/experience metadata when available
- Timestamped recommendation history
- Ranked job recommendations with matched and missing skills

The recommendation flow is intentionally simple at this stage so it can be tested and improved incrementally before adding semantic embeddings.



## Run the project locally

### 1. Start PostgreSQL and Redis

From the repository root:

```powershell
docker compose -f infra/docker/docker-compose.yml up -d
```

### 2. Start the API

```powershell
cd services/api
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### 3. Add demo data

In a second terminal, from the repository root:

```powershell
python scripts/seed_demo_data.py
```

This creates a demo candidate and a small local job dataset so the recommendation flow can be tested without depending on an external job API.

### 4. Start the dashboard

In another terminal:

```powershell
cd apps/web
npm install
npm run dev
```

Dashboard: http://localhost:3000

The dashboard can create a candidate profile, upload a resume, show ranked jobs, filter them, explain matched/missing skills, highlight skill gaps, link to learning resources, save jobs, track application status, review application analytics and recommendation history, and configure match-score alerts.

### Current product flow

```text
Resume / Profile
      ↓
Skill Extraction
      ↓
Job Normalization
      ↓
Candidate ↔ Job Matching
      ↓
Ranked Recommendations
      ↓
Skill Gap Analysis
      ↓
Learning Resources
      ↓
Web Dashboard
```


## What makes the matching "AI"

The first version deliberately uses an explainable hybrid baseline instead of a black-box model:

- **Skill overlap:** measures how many job skills are already present.
- **TF-IDF similarity:** compares resume text with the job title/description.
- **Role preference:** checks whether a preferred role appears in the title.
- **Location preference:** checks the candidate's preferred location.
- **Experience compatibility:** gives a small bonus when the candidate fits the job's stated experience range.

The weighted score is currently:

`50% skills + 20% resume/job text similarity + 15% role + 10% location + 5% experience`

This gives the project a measurable ML baseline that can later be compared with sentence-transformer embeddings.

## Candidate workflow

1. Create a candidate profile.
2. Upload a PDF, DOCX, or TXT resume.
3. Extract and normalize skills.
4. Ingest normalized jobs through source adapters.
5. Rank jobs with the hybrid matcher.
6. Inspect matched and missing skills.
7. Review the highest-priority skill gaps.
8. Open curated learning resources.
9. Save interesting jobs and track application status.

## Current API areas

- `/auth/register`, `/auth/login`, `/auth/me`
  - JWT authentication with password hashing
- `/candidates`
- `/candidates/{candidate_id}/resumes`
- `/jobs`
- `/recommendations/{candidate_id}`
- `/matches/{candidate_id}/{job_id}`
- `/skill-gaps/{candidate_id}`
- `/learning`
- `/tracking/saved`
- `/tracking/applications`
- `/alerts`

The demo job source is intentionally local. Real job adapters can be added independently and should use permitted APIs, feeds, or public career endpoints rather than scraping sites that prohibit it.


## Current implementation status

The current baseline includes a working explainable recommendation flow, resume parsing, normalized job ingestion, search/filtering, skill-gap analysis, learning resources, saved jobs, application tracking, recommendation history, application analytics, and threshold-based job alerts. Job creation and ingestion writes require an authenticated account; public job reads remain available for the dashboard. The default matcher remains intentionally explainable: skills (50%), TF-IDF text similarity (20%), preferred role (15%), location (10%), and experience compatibility (5%). Optional sentence-transformer semantic matching and an evaluation suite are also included.

### What is deliberately not claimed yet

- No live external job provider is bundled by default; the demo source is local.
- Alerts are checked on demand and by the scheduled ingestion worker. Optional SMTP email delivery is implemented; push notifications are not implemented.
- Semantic embeddings remain optional rather than required for the default local setup. They can be compared against the TF-IDF/hybrid baseline using the evaluation utilities in `ml/matching`.



## One-command local startup

With Docker Desktop running, Windows users can start the full stack with:

```powershell
.\scripts\start-all.ps1
```

Or from any shell:

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

The Compose stack starts PostgreSQL, Redis, FastAPI, Next.js, and a scheduler-friendly
ingestion service. API readiness is checked before the web and scheduler services start. PostgreSQL and Redis use healthchecks, and the API waits for
PostgreSQL/Redis readiness before starting. Docker Compose supports healthcheck-based
`depends_on` conditions for this startup pattern.

The scheduler runs the configured public job source every 6 hours by default
(`INGEST_INTERVAL_MINUTES=360`). Change that environment value if you want a different
interval.

## Matching evaluation

The repository now includes a labelled dataset at `ml/matching/evaluation_dataset.json`
with multiple candidate/job ranking cases. The evaluation utilities compare:

- TF-IDF lexical similarity
- Sentence-transformer semantic similarity
- A simple hybrid of lexical + semantic similarity

Metrics include Precision@K, Recall@K, NDCG@K, and MRR.

Run the report from the repository root after installing the optional semantic dependency:

```powershell
cd services/api
pip install -e ".[semantic]"
cd ../..
$env:PYTHONPATH="."
python ml/matching/evaluation_report.py
```

The benchmark is intentionally a small labelled dataset, so its numbers are useful for
project experimentation rather than a claim of production-grade model performance.

## Recommendation history

Every manual recommendation refresh gets a unique run ID and is retained in the
`recommendations` table. History can be inspected through:

```text
GET /recommendations/{candidate_id}/history
```

This lets the project evolve from a one-shot ranking demo toward measuring how
recommendations change as a candidate profile or job dataset changes.

## Current alert behavior

The scheduled ingestion runner evaluates enabled match-score alerts immediately after
ingestion and records each alert/job detection once. Optional SMTP email delivery is implemented on top of that detection state; push notifications are not implemented. Notification delivery is kept separate from the matching engine.


### Authentication

The app now supports account registration and login. The API issues configurable-expiry JWT bearer tokens and stores only password hashes. Candidate-specific APIs verify that the authenticated account owns the requested candidate profile.

For local development, scripts/seed_demo_data.py also creates:
- Email: demo@aijobmatch.local
- Password: Demo12345!

### Email alerts

Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM, and SMTP_USE_TLS to enable email delivery from the scheduled ingestion worker. Without SMTP configuration, alert detection still works in the dashboard/API but no email is sent.

### Current recommendation scoring

| Component | Weight |
| --- | ---: |
| Skill overlap | 50% |
| Resume/job text similarity | 20% |
| Preferred role | 15% |
| Location | 10% |
| Experience compatibility | 5% |


## Security and validation notes

- Candidate-specific recommendation, tracking, alert, resume, and profile endpoints enforce authenticated candidate ownership.
- Job write/ingestion endpoints require authentication; job detail/list reads remain public for the dashboard.
- Passwords are stored as Argon2 hashes rather than plaintext.
- Alert detections are deduplicated by alert + job, even when SMTP email delivery is disabled.
- The repository includes regression coverage for authentication helpers, candidate serialization, recommendation history, alert deduplication, experience compatibility, job filters, ingestion, and matching behavior.
- GitHub Actions checks Python lint/tests, the Next.js production build, and Docker Compose configuration on pushes and pull requests.

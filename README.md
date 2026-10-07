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
packages/
  shared/              # shared schemas/constants
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

Phase 1 — foundation and architecture.

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
- PostgreSQL + pgvector
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

The dashboard can create a candidate profile, upload a resume, show ranked jobs, explain matched/missing skills, highlight skill gaps, and link to learning resources.

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

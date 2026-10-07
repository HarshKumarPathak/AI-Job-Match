# AI Job Match API

FastAPI backend for candidate profiles, resume processing, jobs, and recommendations.

## Local development

From this directory:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

The PostgreSQL and Redis development services are defined in `../../infra/docker/docker-compose.yml`.

FROM python:3.12-slim
WORKDIR /app
COPY services/api/pyproject.toml services/api/
COPY services/api/app services/api/app
COPY services/api/alembic.ini services/api/
COPY services/api/alembic services/api/alembic
COPY services/api/data services/api/data
COPY services/worker services/worker
RUN pip install --no-cache-dir ./services/api
ENV PYTHONPATH=/app/services/api
CMD ["python", "services/worker/run_ingestion.py", "--source", "arbeitnow"]

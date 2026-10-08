FROM python:3.12-slim
WORKDIR /app
COPY services/api/pyproject.toml ./
COPY services/api/app ./app
COPY services/api/alembic.ini ./
COPY services/api/alembic ./alembic
COPY services/api/data ./data
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

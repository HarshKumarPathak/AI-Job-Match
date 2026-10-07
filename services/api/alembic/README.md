# Alembic migrations

Run from `services/api`:

```bash
alembic upgrade head
```

Create a new revision after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe change"
```

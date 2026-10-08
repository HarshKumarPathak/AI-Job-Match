from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_job_match"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-development"
    matching_text_model: str = "tfidf"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

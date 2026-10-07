from fastapi import FastAPI

app = FastAPI(
    title="AI Job Match API",
    version="0.1.0",
    description="Job aggregation, recommendation, and skill-gap analysis API.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-job-match-api"}

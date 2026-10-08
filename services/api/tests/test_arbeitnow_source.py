from app.services.arbeitnow_source import ArbeitnowJobSource


def test_arbeitnow_source_normalizes_api_payload(monkeypatch) -> None:
    payload = {
        "data": [
            {
                "slug": "python-backend-1",
                "title": "Python Backend Engineer",
                "company_name": "Example",
                "description": "<p>Build APIs with Python, FastAPI and SQL.</p>",
                "location": "Remote",
                "remote": True,
                "url": "https://example.com/job",
                "job_types": ["full-time"],
            }
        ]
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            import json
            return json.dumps(payload).encode()

    monkeypatch.setattr("app.services.arbeitnow_source.urlopen", lambda *args, **kwargs: FakeResponse())

    jobs = ArbeitnowJobSource().fetch_jobs()

    assert len(jobs) == 1
    assert jobs[0]["external_id"] == "python-backend-1"
    assert jobs[0]["source"] == "arbeitnow"
    assert jobs[0]["remote"] is True
    assert "python" in jobs[0]["skills"]
    assert "fastapi" in jobs[0]["skills"]

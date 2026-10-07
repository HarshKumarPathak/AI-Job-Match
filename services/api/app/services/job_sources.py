from pathlib import Path
import json
from typing import Protocol


class JobSource(Protocol):
    name: str

    def fetch_jobs(self) -> list[dict]:
        ...


class DemoJobSource:
    name = "demo"

    def fetch_jobs(self) -> list[dict]:
        path = Path(__file__).resolve().parents[2] / "data" / "demo_jobs.json"
        return json.loads(path.read_text(encoding="utf-8"))

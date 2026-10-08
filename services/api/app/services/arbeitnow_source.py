import html
import json
from urllib.request import Request, urlopen

from app.services.skill_extractor import extract_skills
from app.services.skill_normalization import normalize_skills


class ArbeitnowJobSource:
    """Adapter for Arbeitnow's documented free job-board API."""

    name = "arbeitnow"

    def __init__(self, url: str = "https://www.arbeitnow.com/api/job-board-api?page=1") -> None:
        self.url = url

    def fetch_jobs(self) -> list[dict]:
        request = Request(self.url, headers={"User-Agent": "AI-Job-Match/1.0"})
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)

        jobs: list[dict] = []
        for item in payload.get("data", []):
            description = html.unescape(item.get("description", ""))
            title = html.unescape(item.get("title", ""))
            company = html.unescape(item.get("company_name", ""))
            jobs.append(
                {
                    "external_id": item.get("slug"),
                    "title": title,
                    "company": company,
                    "description": description,
                    "location": item.get("location"),
                    "remote": bool(item.get("remote", False)),
                    "employment_type": ", ".join(item.get("job_types", [])) or None,
                    "apply_url": item.get("url"),
                    "source": self.name,
                    "skills": normalize_skills(extract_skills(f"{title} {description}")),
                    "salary_min": item.get("salary_min"),
                    "salary_max": item.get("salary_max"),
                    "experience_min_years": item.get("experience_min_years"),
                    "experience_max_years": item.get("experience_max_years"),
                }
            )

        return jobs

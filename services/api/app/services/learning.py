from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LearningResource:
    skill: str
    level: str
    resource_type: str
    title: str
    url: str


RESOURCE_CATALOG = {
    "python": LearningResource("python", "beginner", "documentation", "Python Tutorial", "https://docs.python.org/3/tutorial/"),
    "sql": LearningResource("sql", "beginner", "practice", "SQLBolt", "https://sqlbolt.com/"),
    "postgresql": LearningResource("postgresql", "beginner", "documentation", "PostgreSQL Tutorial", "https://www.postgresql.org/docs/current/tutorial.html"),
    "docker": LearningResource("docker", "beginner", "documentation", "Docker Get Started", "https://docs.docker.com/get-started/"),
    "fastapi": LearningResource("fastapi", "beginner", "documentation", "FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/"),
    "machine learning": LearningResource("machine learning", "beginner", "course", "Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course"),
    "javascript": LearningResource("javascript", "beginner", "documentation", "MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
    "typescript": LearningResource("typescript", "beginner", "documentation", "TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "react": LearningResource("react", "beginner", "documentation", "React Learn", "https://react.dev/learn"),
    "git": LearningResource("git", "beginner", "documentation", "Git Documentation", "https://git-scm.com/doc"),
}


def resources_for_skills(skills: list[str]) -> list[LearningResource]:
    return [
        resource
        for skill in skills
        if (resource := RESOURCE_CATALOG.get(skill))
    ]

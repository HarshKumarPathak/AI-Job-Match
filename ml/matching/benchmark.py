"""Small labelled benchmark for comparing lexical and semantic ranking."""

from dataclasses import dataclass
import json
from pathlib import Path

from ml.matching.evaluation import ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank
from ml.matching.tfidf_baseline import similarity as tfidf_similarity


@dataclass(frozen=True, slots=True)
class Example:
    candidate: str
    jobs: tuple[str, ...]
    relevant: set[str]


EXAMPLES = (
    Example("Python machine learning NLP backend development", ("Python backend API development", "Machine learning NLP engineer", "Frontend React developer", "Sales operations analyst"), {"1"}),
    Example("SQL data analysis pandas dashboards", ("React frontend engineer", "Data analyst SQL pandas", "Java Android developer", "Graphic designer"), {"1"}),
)


def evaluate(model_name: str, scorer) -> dict[str, float | str]:
    rows = []
    for example in load_dataset():
        scored = [(str(index), scorer(example.candidate, job)) for index, job in enumerate(example.jobs)]
        ranked = [index for index, _ in sorted(scored, key=lambda item: item[1], reverse=True)]
        rows.append({"precision@3": precision_at_k(example.relevant, ranked, 3), "recall@3": recall_at_k(example.relevant, ranked, 3), "ndcg@3": ndcg_at_k(example.relevant, ranked, 3), "mrr": reciprocal_rank(example.relevant, ranked)})
    return {"model": model_name, **{metric: round(sum(row[metric] for row in rows) / len(rows), 4) for metric in rows[0]}}


def run_benchmark() -> list[dict[str, float | str]]:
    results = [evaluate("tfidf", tfidf_similarity)]
    try:
        from ml.matching.semantic import similarity as semantic_similarity
    except ImportError:
        return results
    results.append(evaluate("semantic", semantic_similarity))
    return results


if __name__ == "__main__":
    for row in run_benchmark():
        print(row)

def load_dataset() -> tuple[Example, ...]:
    path = Path(__file__).with_name("evaluation_dataset.json")
    rows = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        Example(row["candidate"], tuple(row["jobs"]), set(row["relevant"]))
        for row in rows
    )

"""Small, reproducible comparison helpers for matching models."""

from dataclasses import dataclass
from typing import Callable

from ml.matching.tfidf_baseline import similarity as tfidf_similarity


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    model: str
    score: float


def compare_similarity(candidate_text: str, job_text: str, semantic_similarity: Callable[[str, str], float] | None = None) -> list[SimilarityResult]:
    results = [SimilarityResult("tfidf", tfidf_similarity(candidate_text, job_text))]
    if semantic_similarity is not None:
        results.append(SimilarityResult("semantic", semantic_similarity(candidate_text, job_text)))
    return results
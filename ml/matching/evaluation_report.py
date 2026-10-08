"""Reproducible ranking evaluation with TF-IDF, semantic and hybrid scorers."""

from ml.matching.benchmark import load_dataset
from ml.matching.evaluation import ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank
from ml.matching.tfidf_baseline import similarity as tfidf_similarity


def evaluate(name, scorer, k=3):
    metrics = []
    for example in load_dataset():
        ranked = [
            str(i) for i, _ in sorted(
                ((i, scorer(example.candidate, job)) for i, job in enumerate(example.jobs)),
                key=lambda item: item[1],
                reverse=True,
            )
        ]
        metrics.append({
            "precision@k": precision_at_k(example.relevant, ranked, k),
            "recall@k": recall_at_k(example.relevant, ranked, k),
            "ndcg@k": ndcg_at_k(example.relevant, ranked, k),
            "mrr": reciprocal_rank(example.relevant, ranked),
        })
    return {
        "model": name,
        **{key: round(sum(row[key] for row in metrics) / len(metrics), 4) for key in metrics[0]},
    }

def run_report():
    results = [evaluate("tfidf", tfidf_similarity)]
    try:
        from ml.matching.semantic import similarity as semantic_similarity
    except ImportError:
        return results

    def hybrid(candidate: str, job: str) -> float:
        return 0.55 * tfidf_similarity(candidate, job) + 0.45 * semantic_similarity(candidate, job)

    results.append(evaluate("semantic", semantic_similarity))
    results.append(evaluate("hybrid", hybrid))
    return results

if __name__ == "__main__":
    for row in run_report():
        print(row)

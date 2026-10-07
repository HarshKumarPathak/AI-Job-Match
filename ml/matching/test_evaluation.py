from ml.matching.evaluation import ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank


def test_ranking_metrics() -> None:
    relevant = {"a", "c"}
    ranked = ["b", "a", "c", "d"]

    assert precision_at_k(relevant, ranked, 2) == 0.5
    assert recall_at_k(relevant, ranked, 2) == 0.5
    assert reciprocal_rank(relevant, ranked) == 0.5
    assert round(ndcg_at_k(relevant, ranked, 3), 3) == 0.693

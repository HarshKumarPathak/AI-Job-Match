from ml.matching.model_comparison import compare_similarity


def test_model_comparison_always_has_tfidf_baseline() -> None:
    results = compare_similarity("python backend", "python api")
    assert results[0].model == "tfidf"
    assert 0 <= results[0].score <= 1


def test_model_comparison_can_include_semantic_scorer() -> None:
    results = compare_similarity("python backend", "python api", semantic_similarity=lambda left, right: 0.81)
    assert [(item.model, item.score) for item in results] == [("tfidf", results[0].score), ("semantic", 0.81)]
from ml.matching.tfidf_baseline import similarity


def test_tfidf_empty_text_is_zero() -> None:
    assert similarity("", "python") == 0.0
    assert similarity("python", "") == 0.0


def test_tfidf_related_text_has_similarity() -> None:
    score = similarity("python machine learning", "python machine learning engineer")
    assert 0 < score <= 1
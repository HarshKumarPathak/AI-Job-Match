"""Optional semantic text similarity using sentence-transformers."""

from functools import lru_cache


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Semantic matching requires sentence-transformers. "
            'Install with: pip install -e "services/api[semantic]"'
        ) from exc
    return SentenceTransformer(model_name)


def similarity(candidate_text: str, job_text: str, model_name: str = "all-MiniLM-L6-v2") -> float:
    """Return cosine similarity in the [0, 1] range."""
    if not candidate_text.strip() or not job_text.strip():
        return 0.0
    model = _load_model(model_name)
    embeddings = model.encode([candidate_text, job_text], normalize_embeddings=True)
    score = float(embeddings[0] @ embeddings[1])
    return max(0.0, min(1.0, score))
"""Optional semantic similarity service for the API."""

from functools import lru_cache


@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            'Semantic matching requires the optional dependency. Install with: pip install -e ".[semantic]"'
        ) from exc
    return SentenceTransformer("all-MiniLM-L6-v2")


def similarity(left: str, right: str) -> float:
    if not left.strip() or not right.strip():
        return 0.0
    model = _model()
    embeddings = model.encode([left, right], normalize_embeddings=True)
    score = float(embeddings[0] @ embeddings[1])
    return max(0.0, min(1.0, score))

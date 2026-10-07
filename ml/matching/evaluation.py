from math import log2


def precision_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    top = ranked[:k]
    if not top:
        return 0.0
    return sum(item in relevant for item in top) / len(top)


def recall_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(item in relevant for item in ranked[:k]) / len(relevant)


def reciprocal_rank(relevant: set[str], ranked: list[str]) -> float:
    for index, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1.0 / index
    return 0.0


def ndcg_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    top = ranked[:k]
    dcg = sum(1.0 / log2(index + 2) for index, item in enumerate(top) if item in relevant)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / log2(index + 2) for index in range(ideal_hits))
    return dcg / idcg if idcg else 0.0

"""Simple lexical baseline used to establish a measurable first model."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def similarity(candidate_text: str, job_text: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([candidate_text, job_text])
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])

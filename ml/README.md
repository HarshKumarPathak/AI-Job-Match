# ML Layer

The ML layer contains independent components for:

- resume/entity extraction
- skill normalization
- TF-IDF baseline matching
- semantic embeddings
- hybrid recommendation
- skill-gap prioritization

The first matching implementation should establish a measurable lexical baseline before adding embeddings.


## Matching experiments

The `ml/matching` package now contains the TF-IDF baseline, optional `sentence-transformers` semantic similarity, ranking metrics, and a small labelled benchmark for comparing model behaviour. Semantic dependencies are optional so the normal API installation stays lightweight.

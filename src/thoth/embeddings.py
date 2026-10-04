from __future__ import annotations

import numpy as np
import hashlib

from thoth.contracts import Observation

MODEL = "spaCy/en_core_web_md"


def pedagogical_text(observation: Observation) -> str:
    # Behavior/outcome/quote can vary as availability improves. Embed the ability
    # and purpose, not incidental topics or the fact that one attempt failed.
    return observation.learning_dimension + ". " + observation.communicative_intent


class LocalEmbedder:
    def __init__(self):
        import spacy
        import en_core_web_md
        self.nlp = spacy.load("en_core_web_md", exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
        weights = hashlib.sha256(self.nlp.vocab.vectors.data.tobytes()).hexdigest()
        self.model = MODEL + ":" + weights[:16]
        self.metadata = {"model": MODEL, "package": en_core_web_md.__version__, "weights_sha256": weights,
                         "dimensions": self.nlp.vocab.vectors_length, "pooling": "mean of nonzero token vectors; L2 normalized"}

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        result = []
        for text in texts:
            vectors = [token.vector for token in self.nlp.make_doc(text) if token.has_vector and not token.is_punct and not token.is_space]
            if not vectors:
                raise ValueError("Embedding has no known tokens; supply an English pedagogical description")
            vector = np.mean(vectors, axis=0).astype("<f4")
            norm = float(np.linalg.norm(vector))
            if not np.isfinite(norm) or norm <= 0:
                raise ValueError("Invalid embedding")
            result.append(vector / norm)
        return result


def blob(vector: np.ndarray) -> bytes:
    value = np.asarray(vector, dtype="<f4")
    if value.ndim != 1 or not np.all(np.isfinite(value)) or not np.isclose(np.linalg.norm(value), 1, atol=1e-5):
        raise ValueError("Expected a finite normalized one-dimensional vector")
    return value.tobytes()


def unblob(value: bytes) -> np.ndarray:
    return np.frombuffer(value, dtype="<f4")

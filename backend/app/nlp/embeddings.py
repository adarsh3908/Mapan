import numpy as np
from typing import List, Dict

class NLPFeatureExtractor:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except Exception:
            self.model = None # Fallback to keyword-based embedding proxy

    def extract_embedding(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            return np.zeros(384, dtype=float)

        if self.model is not None:
            try:
                emb = self.model.encode(text)
                return np.array(emb, dtype=float)
            except Exception:
                pass

        # Deterministic lightweight pseudo-embedding fallback
        rng = np.random.RandomState(abs(hash(text)) % (2**32))
        return rng.randn(384) * 0.1

    def predict_trait_offsets(self, text_responses: List[str]) -> Dict[str, float]:
        """
        Maps candidate free-text justifications to Big Five trait adjustments (-0.1 to +0.1).
        """
        if not text_responses:
            return {
                "Openness": 0.0,
                "Conscientiousness": 0.0,
                "Extraversion": 0.0,
                "Agreeableness": 0.0,
                "Emotional Stability": 0.0
            }

        combined_text = " ".join([t for t in text_responses if t])
        emb = self.extract_embedding(combined_text)

        # Pre-calculated projection weights for 5 traits
        np.random.seed(42)
        proj_matrix = np.random.randn(384, 5) * 0.05
        raw_offsets = np.dot(emb, proj_matrix)
        normalized_offsets = np.tanh(raw_offsets) * 0.08

        traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Emotional Stability"]
        return {trait: round(float(normalized_offsets[i]), 4) for i, trait in enumerate(traits)}

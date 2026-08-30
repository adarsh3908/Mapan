import pytest
from backend.app.fit_engine.matcher import FitEngine

def test_fit_engine_computation():
    engine = FitEngine(se_reliability_threshold=0.15)
    candidate_traits = {
        "Conscientiousness": {"score": 0.85, "se": 0.05},
        "Openness": {"score": 0.80, "se": 0.06},
        "Emotional Stability": {"score": 0.75, "se": 0.08},
        "Agreeableness": {"score": 0.65, "se": 0.18}, # Above 0.15 threshold -> Low evidence
        "Extraversion": {"score": 0.50, "se": 0.09}
    }

    role_reqs = [
        {"trait_name": "Conscientiousness", "target_level": 0.85, "weight": 1.2},
        {"trait_name": "Openness", "target_level": 0.80, "weight": 1.1},
        {"trait_name": "Emotional Stability", "target_level": 0.75, "weight": 1.0},
        {"trait_name": "Agreeableness", "target_level": 0.65, "weight": 0.8},
        {"trait_name": "Extraversion", "target_level": 0.50, "weight": 0.6}
    ]

    fit_res = engine.compute_fit(candidate_traits, role_reqs)
    assert 90.0 <= fit_res["fit_score"] <= 100.0 # High match should yield near 100 fit score
    assert fit_res["confidence_interval_low"] <= fit_res["fit_score"] <= fit_res["confidence_interval_high"]
    assert "Agreeableness" in fit_res["low_evidence_traits"]

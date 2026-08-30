import pytest
import numpy as np
from backend.app.psychometrics.ctt import calculate_cronbach_alpha, calculate_mcdonald_omega, compute_ctt_trait_scores
from backend.app.psychometrics.irt import compute_irt_trait_scores

def test_cronbach_alpha_calculation():
    # Synthetic responses: 5 persons, 4 items with high internal consistency
    data = np.array([
        [1, 1, 1, 1],
        [1, 1, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [1, 1, 1, 0]
    ])
    alpha = calculate_cronbach_alpha(data)
    assert 0.0 <= alpha <= 1.0
    assert alpha > 0.5 # High internal consistency should yield alpha > 0.5

def test_mcdonald_omega_calculation():
    data = np.array([
        [1, 1, 1, 1],
        [1, 1, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [1, 1, 1, 0]
    ])
    omega = calculate_mcdonald_omega(data)
    assert 0.0 <= omega <= 1.0

def test_compute_ctt_trait_scores():
    item_scores = {
        "Conscientiousness": [0.8, 0.9, 0.85, 0.75],
        "Emotional Stability": [0.6, 0.7, 0.65]
    }
    results = compute_ctt_trait_scores(item_scores)
    assert "Conscientiousness" in results
    assert 0.7 <= results["Conscientiousness"]["score"] <= 0.95
    assert results["Conscientiousness"]["se"] > 0.0

def test_compute_irt_trait_scores():
    item_responses = {
        "Conscientiousness": [1, 1, 0, 1],
        "Extraversion": [0, 1, 0, 0]
    }
    results = compute_irt_trait_scores(item_responses)
    assert "Conscientiousness" in results
    assert "Extraversion" in results

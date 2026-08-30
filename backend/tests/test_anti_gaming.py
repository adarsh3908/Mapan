import pytest
from backend.app.anti_gaming.harness import AntiGamingHarness

def test_anti_gaming_harness():
    harness = AntiGamingHarness()
    honest_payload = {
        "self_report_scores": {
            "Conscientiousness": 0.60,
            "Emotional Stability": 0.65,
            "Agreeableness": 0.70,
            "Extraversion": 0.55,
            "Openness": 0.75
        },
        "sjt_item_scores": {
            "Conscientiousness": [0.65, 0.70],
            "Emotional Stability": [0.60, 0.65],
            "Agreeableness": [0.70],
            "Extraversion": [0.55],
            "Openness": [0.75]
        },
        "response_latencies_ms": {"item_1": 4500.0, "item_2": 3800.0},
        "forced_choice_consistency": 0.90,
        "free_text_justifications": ["I took time to evaluate the situation."]
    }

    report = harness.evaluate_faking_robustness(honest_payload)
    assert len(report) == 7
    # Model 7 (Fused) should show less faking shift than Model 1 (Self Report Baseline)
    m1_shift = report["model_1"]["mean_faking_shift"]
    m7_shift = report["model_7"]["mean_faking_shift"]
    assert m7_shift < m1_shift
    assert report["model_7"]["faking_resistance_rating"] in ["High", "Moderate"]

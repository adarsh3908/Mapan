import pytest
from backend.app.fusion.ablation_runner import AblationEngine

def test_ablation_models_execution():
    engine = AblationEngine()
    payload = {
        "self_report_scores": {
            "Conscientiousness": 0.8,
            "Emotional Stability": 0.7,
            "Agreeableness": 0.75,
            "Extraversion": 0.6,
            "Openness": 0.85
        },
        "sjt_item_scores": {
            "Conscientiousness": [0.8, 0.85, 0.9],
            "Emotional Stability": [0.7, 0.75],
            "Agreeableness": [0.8],
            "Extraversion": [0.65],
            "Openness": [0.8]
        },
        "response_latencies_ms": {"item_1": 3500.0, "item_2": 4200.0},
        "forced_choice_consistency": 0.88,
        "free_text_justifications": ["I ensured thorough verification before release."]
    }

    all_results = engine.run_all_models(payload)
    assert len(all_results) == 7

    for i in range(1, 8):
        tag = f"model_{i}"
        assert tag in all_results
        model_out = all_results[tag]
        assert "Conscientiousness" in model_out
        assert 0.0 <= model_out["Conscientiousness"]["score"] <= 1.0
        assert model_out["Conscientiousness"]["se"] > 0.0

    # Model 7 (Full Fused) should have lower standard error than Model 1 (Self Report Baseline)
    m1_se = all_results["model_1"]["Conscientiousness"]["se"]
    m7_se = all_results["model_7"]["Conscientiousness"]["se"]
    assert m7_se < m1_se

import pytest
from backend.app.fairness.audit import FairnessAuditGate

def test_fairness_audit_gate():
    gate = FairnessAuditGate(max_allowable_gap=5.0)

    # Balanced candidate dataset (small gap <= 5.0)
    records_pass = [
        {"demographics": {"gender": "Male", "age": 28, "region": "North"}, "fit_score": 82.0},
        {"demographics": {"gender": "Female", "age": 30, "region": "North"}, "fit_score": 84.0},
        {"demographics": {"gender": "Male", "age": 40, "region": "South"}, "fit_score": 81.0},
        {"demographics": {"gender": "Female", "age": 24, "region": "South"}, "fit_score": 83.5}
    ]

    res_pass = gate.run_subgroup_audit(records_pass)
    assert res_pass["overall_fairness_passed"] is True
    assert res_pass["subgroup_breakdown"]["gender"]["max_score_gap"] <= 5.0

    # Imbalanced candidate dataset (large gap > 5.0)
    records_fail = [
        {"demographics": {"gender": "Male", "age": 28, "region": "North"}, "fit_score": 92.0},
        {"demographics": {"gender": "Female", "age": 30, "region": "North"}, "fit_score": 75.0}
    ]

    res_fail = gate.run_subgroup_audit(records_fail)
    assert res_fail["overall_fairness_passed"] is False
    assert res_fail["subgroup_breakdown"]["gender"]["max_score_gap"] > 5.0

import numpy as np
from typing import List, Dict, Any

class FairnessAuditGate:
    """
    Standalone Fairness Audit Gate (FR6 / Patent Core Module).
    Audits assessment outputs for subgroup performance gaps and demographic parity.
    """
    def __init__(self, max_allowable_gap: float = 5.0):
        self.max_allowable_gap = max_allowable_gap # Maximum 5% allowable score gap

    def run_subgroup_audit(self, candidate_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        candidate_records: list of dicts containing:
        - 'demographics': {'gender': str, 'age': int, 'region': str}
        - 'fit_score': float
        """
        if not candidate_records:
            return {"status": "NO_DATA", "passed": True, "subgroup_breakdown": {}}

        subgroup_groups: Dict[str, Dict[str, List[float]]] = {
            "gender": {},
            "age_bracket": {},
            "region": {}
        }

        for rec in candidate_records:
            demo = rec.get("demographics", {})
            score = rec.get("fit_score", 50.0)

            # 1. Gender subgrouping
            gender = str(demo.get("gender", "Unspecified"))
            subgroup_groups["gender"].setdefault(gender, []).append(score)

            # 2. Age bracket subgrouping
            age = demo.get("age")
            if age is not None:
                bracket = "< 25" if age < 25 else ("25-34" if age <= 34 else "35+")
            else:
                bracket = "Unspecified"
            subgroup_groups["age_bracket"].setdefault(bracket, []).append(score)

            # 3. Region subgrouping
            region = str(demo.get("region", "Unspecified"))
            subgroup_groups["region"].setdefault(region, []).append(score)

        breakdown = {}
        all_passed = True

        for category, groups in subgroup_groups.items():
            cat_stats = {}
            means = []

            for group_name, scores in groups.items():
                if not scores:
                    continue
                mean_s = float(np.mean(scores))
                std_s = float(np.std(scores)) if len(scores) > 1 else 0.0
                cat_stats[group_name] = {
                    "count": len(scores),
                    "mean_fit_score": round(mean_s, 2),
                    "std_dev": round(std_s, 2)
                }
                means.append(mean_s)

            if len(means) > 1:
                max_gap = float(max(means) - min(means))
            else:
                max_gap = 0.0

            passed = max_gap <= self.max_allowable_gap
            if not passed:
                all_passed = False

            breakdown[category] = {
                "groups": cat_stats,
                "max_score_gap": round(max_gap, 2),
                "threshold": self.max_allowable_gap,
                "passed": passed
            }

        return {
            "status": "AUDITED",
            "overall_fairness_passed": all_passed,
            "subgroup_breakdown": breakdown
        }

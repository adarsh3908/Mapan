import numpy as np
from typing import Dict, List, Any

class FitEngine:
    def __init__(self, se_reliability_threshold: float = 0.15):
        self.se_reliability_threshold = se_reliability_threshold

    def compute_fit(
        self,
        candidate_traits: Dict[str, Dict[str, float]],
        role_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        candidate_traits: dict mapping trait_name -> {'score': float, 'se': float}
        role_requirements: list of dicts with 'trait_name', 'target_level', 'weight'
        Returns fit_score (0..100), confidence_interval_low/high, and low_evidence_traits.
        """
        if not role_requirements:
            return {
                "fit_score": 50.0,
                "confidence_interval_low": 40.0,
                "confidence_interval_high": 60.0,
                "low_evidence_traits": [],
                "trait_breakdown": {}
            }

        weighted_dist_sq = 0.0
        total_weight = 0.0
        trait_breakdown = {}
        low_evidence_traits = []
        se_variances = []

        for req in role_requirements:
            trait = req["trait_name"]
            target = req["target_level"]
            weight = req.get("weight", 1.0)

            cand = candidate_traits.get(trait, {"score": 0.5, "se": 0.2})
            score = cand["score"]
            se = cand["se"]

            if se > self.se_reliability_threshold:
                low_evidence_traits.append(trait)

            diff = score - target
            dist_sq = (diff ** 2) * weight
            weighted_dist_sq += dist_sq
            total_weight += weight

            se_variances.append((se * weight) ** 2)

            trait_breakdown[trait] = {
                "candidate_score": round(score, 4),
                "target_level": round(target, 4),
                "delta": round(diff, 4),
                "weight": weight,
                "standard_error": round(se, 4)
            }

        if total_weight == 0:
            total_weight = 1.0

        # Normalized root mean weighted squared distance
        rms_dist = np.sqrt(weighted_dist_sq / total_weight)
        # Convert distance (0..1 scale) to fit index (0..100)
        fit_score = float(np.clip((1.0 - rms_dist) * 100.0, 0.0, 100.0))

        # Error propagation into confidence interval bounds
        combined_se = np.sqrt(np.sum(se_variances)) / total_weight
        ci_margin = float(1.96 * combined_se * 100.0)

        ci_low = float(np.clip(fit_score - ci_margin, 0.0, 100.0))
        ci_high = float(np.clip(fit_score + ci_margin, 0.0, 100.0))

        return {
            "fit_score": round(fit_score, 2),
            "confidence_interval_low": round(ci_low, 2),
            "confidence_interval_high": round(ci_high, 2),
            "low_evidence_traits": low_evidence_traits,
            "trait_breakdown": trait_breakdown
        }

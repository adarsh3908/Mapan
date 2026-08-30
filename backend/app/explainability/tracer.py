from typing import Dict, List, Any

class ExplainabilityTracer:
    """
    Confidence & Explainability Layer.
    Traces every fit score back to contributing trait evidence and SJT responses.
    """
    def generate_explanation(
        self,
        role_title: str,
        fit_result: Dict[str, Any],
        candidate_traits: Dict[str, Dict[str, float]],
        item_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        fit_score = fit_result.get("fit_score", 0.0)
        ci_low = fit_result.get("confidence_interval_low", 0.0)
        ci_high = fit_result.get("confidence_interval_high", 0.0)
        low_evidence = fit_result.get("low_evidence_traits", [])
        breakdown = fit_result.get("trait_breakdown", {})

        top_supporting_traits = []
        gaps_and_risks = []

        for trait, details in breakdown.items():
            delta = details.get("delta", 0.0)
            cand_score = details.get("candidate_score", 0.0)
            target = details.get("target_level", 0.0)

            if abs(delta) <= 0.10:
                top_supporting_traits.append({
                    "trait": trait,
                    "assessment": f"Candidate score ({cand_score:.2f}) closely aligns with target requirement ({target:.2f}).",
                    "strength": "High Match"
                })
            elif delta < -0.10:
                gaps_and_risks.append({
                    "trait": trait,
                    "assessment": f"Candidate score ({cand_score:.2f}) is below target requirement ({target:.2f}).",
                    "risk_level": "Moderate Gap" if delta > -0.25 else "Significant Gap"
                })
            elif delta > 0.10:
                top_supporting_traits.append({
                    "trait": trait,
                    "assessment": f"Candidate score ({cand_score:.2f}) exceeds target requirement ({target:.2f}).",
                    "strength": "Exceeds Requirement"
                })

        summary_narrative = (
            f"Candidate achieved an overall occupational fit score of {fit_score:.1f}% "
            f"(95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]) for the {role_title} role. "
            f"{len(top_supporting_traits)} key traits matched or exceeded requirements."
        )

        if low_evidence:
            summary_narrative += f" Note: {', '.join(low_evidence)} had higher standard error and were flagged for low evidence."

        return {
            "role_title": role_title,
            "overall_fit_score": fit_score,
            "confidence_band": f"[{ci_low:.1f}% - {ci_high:.1f}%]",
            "summary_narrative": summary_narrative,
            "top_supporting_traits": top_supporting_traits,
            "gaps_and_risks": gaps_and_risks,
            "low_evidence_flags": low_evidence,
            "item_evidence_count": len(item_responses)
        }

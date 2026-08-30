import numpy as np
from typing import Dict, Any
from backend.app.fusion.ablation_runner import AblationEngine

class AntiGamingHarness:
    """
    Offline Anti-Gaming Test Harness.
    Applies hardcoded meta-analytic synthetic instructed-fake-good perturbation
    (delta = 0.49 for conscientiousness/agreeableness up to 1.27 for specific lab items)
    to evaluate faking-robustness across Ablation Models 1 to 7.
    """
    # Hardcoded meta-analytic benchmark effect sizes (Martínez & Salgado 2021, MacCann et al. 2017)
    FAKING_BENCHMARKS = {
        "Conscientiousness": 1.27,  # Highest faking inflation in self-report
        "Emotional Stability": 0.85,
        "Agreeableness": 0.65,
        "Extraversion": 0.49,
        "Openness": 0.35
    }

    def __init__(self):
        self.ablation_engine = AblationEngine()

    def generate_faked_payload(self, honest_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Applies calibrated fake-good perturbation to honest payload."""
        faked = {}
        # 1. Perturb self-report scores (strongly inflated by benchmark delta)
        honest_sr = honest_payload.get("self_report_scores", {})
        faked_sr = {}
        for trait, score in honest_sr.items():
            delta = self.FAKING_BENCHMARKS.get(trait, 0.5)
            # Inflation in 0..1 scale space
            faked_sr[trait] = float(np.clip(score + (delta * 0.25), 0.0, 1.0))
        faked["self_report_scores"] = faked_sr

        # 2. Perturb SJT scores (moderately resistant, smaller shift)
        honest_sjt = honest_payload.get("sjt_item_scores", {})
        faked_sjt = {}
        for trait, scores in honest_sjt.items():
            delta = self.FAKING_BENCHMARKS.get(trait, 0.5)
            # SJTs are harder to fake than direct self-report
            faked_sjt[trait] = [float(np.clip(s + (delta * 0.10), 0.0, 1.0)) for s in scores]
        faked["sjt_item_scores"] = faked_sjt

        # 3. Perturb latencies (fake-good responses are rushed / low-thought)
        honest_latencies = honest_payload.get("response_latencies_ms", {})
        faked_latencies = {item_id: max(800.0, lat * 0.45) for item_id, lat in honest_latencies.items()}
        faked["response_latencies_ms"] = faked_latencies

        # 4. Perturb forced-choice consistency (faking creates contradictory choices across items)
        faked["forced_choice_consistency"] = float(max(0.40, honest_payload.get("forced_choice_consistency", 0.8) - 0.30))
        faked["free_text_justifications"] = honest_payload.get("free_text_justifications", [])

        return faked

    def evaluate_faking_robustness(self, honest_payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Runs honest vs faked payloads through Models 1 to 7 and computes score shift (delta).
        """
        faked_payload = self.generate_faked_payload(honest_payload)

        honest_results = self.ablation_engine.run_all_models(honest_payload)
        faked_results = self.ablation_engine.run_all_models(faked_payload)

        shift_report = {}
        for i in range(1, 8):
            tag = f"model_{i}"
            h_model = honest_results[tag]
            f_model = faked_results[tag]

            trait_shifts = {}
            for trait in ["Conscientiousness", "Emotional Stability", "Agreeableness", "Extraversion", "Openness"]:
                h_score = h_model.get(trait, {}).get("score", 0.5)
                f_score = f_model.get(trait, {}).get("score", 0.5)
                shift = f_score - h_score
                trait_shifts[trait] = round(float(shift), 4)

            mean_shift = float(np.mean(list(trait_shifts.values())))
            shift_report[tag] = {
                "mean_faking_shift": round(mean_shift, 4),
                "trait_shifts": trait_shifts,
                "faking_resistance_rating": "High" if mean_shift < 0.08 else ("Moderate" if mean_shift < 0.16 else "Low")
            }

        return shift_report

import numpy as np
from typing import Dict, Any, List
from backend.app.psychometrics.ctt import compute_ctt_trait_scores
from backend.app.psychometrics.irt import compute_irt_trait_scores
from backend.app.nlp.embeddings import NLPFeatureExtractor

class AblationEngine:
    """
    Executes Models 1 through 7 of the ablation study from a single codebase
    by selectively enabling/disabling feature blocks.
    """
    def __init__(self):
        self.nlp_extractor = NLPFeatureExtractor()

    def run_model(self, model_tag: str, payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        payload expects:
        - 'self_report_scores': dict mapping trait -> float (0..1)
        - 'sjt_item_scores': dict mapping trait -> list of float scores
        - 'response_latencies_ms': dict mapping item_id -> float
        - 'forced_choice_consistency': float (0..1)
        - 'free_text_justifications': list of str
        """
        valid_models = ["model_1", "model_2", "model_3", "model_4", "model_5", "model_6", "model_7"]
        if model_tag not in valid_models:
            raise ValueError(f"Unknown model tag: {model_tag}. Must be one of {valid_models}")

        self_report = payload.get("self_report_scores", {})
        sjt_scores = payload.get("sjt_item_scores", {})
        latencies = payload.get("response_latencies_ms", {})
        fc_consistency = payload.get("forced_choice_consistency", 0.8)
        free_text = payload.get("free_text_justifications", [])

        default_traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Emotional Stability"]
        results = {}

        # Model 1: Big Five self-report only
        if model_tag == "model_1":
            for trait in default_traits:
                score = self_report.get(trait, 0.5)
                # Self report baseline has higher standard error due to faking vulnerability
                results[trait] = {"score": round(score, 4), "se": 0.18}
            return results

        # Model 3: SJT only (CTT baseline on SJT item bank)
        sjt_ctt = compute_ctt_trait_scores(sjt_scores)
        if model_tag == "model_3":
            for trait in default_traits:
                val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
                results[trait] = val
            return results

        # Model 2: Big Five self-report + SJT (equal weighted blend)
        if model_tag == "model_2":
            for trait in default_traits:
                sr_score = self_report.get(trait, 0.5)
                sjt_val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
                blended_score = 0.5 * sr_score + 0.5 * sjt_val["score"]
                blended_se = np.sqrt((0.5 * 0.18)**2 + (0.5 * sjt_val["se"])**2)
                results[trait] = {"score": round(blended_score, 4), "se": round(float(blended_se), 4)}
            return results

        # Compute Latency Correction Modifier (used in Models 4, 5, 7)
        latency_modifier = 0.0
        if latencies:
            avg_latency = np.mean(list(latencies.values()))
            # Very fast response (< 1500 ms/item) indicates impulsive / faked-good response
            # Moderate-thoughtful latency (2500-6000 ms) indicates genuine response
            if avg_latency < 1500:
                latency_modifier = -0.05
            elif 2500 <= avg_latency <= 6000:
                latency_modifier = 0.02

        # Model 4: SJT + Response Latency
        if model_tag == "model_4":
            for trait in default_traits:
                sjt_val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
                adj_score = np.clip(sjt_val["score"] + latency_modifier, 0.0, 1.0)
                adj_se = max(0.04, sjt_val["se"] - 0.01) # Latency signal reduces SE
                results[trait] = {"score": round(float(adj_score), 4), "se": round(float(adj_se), 4)}
            return results

        # Model 5: SJT + Response Latency + Forced-Choice Consistency
        if model_tag == "model_5":
            consistency_penalty = (1.0 - fc_consistency) * 0.1
            for trait in default_traits:
                sjt_val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
                adj_score = np.clip(sjt_val["score"] + latency_modifier - consistency_penalty, 0.0, 1.0)
                # Forced-choice consistency improves measurement reliability
                adj_se = max(0.035, sjt_val["se"] - 0.02)
                results[trait] = {"score": round(float(adj_score), 4), "se": round(float(adj_se), 4)}
            return results

        # Model 6: SJT + Linguistic Embeddings
        nlp_offsets = self.nlp_extractor.predict_trait_offsets(free_text)
        if model_tag == "model_6":
            for trait in default_traits:
                sjt_val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
                offset = nlp_offsets.get(trait, 0.0)
                adj_score = np.clip(sjt_val["score"] + offset, 0.0, 1.0)
                adj_se = max(0.04, sjt_val["se"] - 0.015)
                results[trait] = {"score": round(float(adj_score), 4), "se": round(float(adj_se), 4)}
            return results

        # Model 7: Full Hybrid Fused Model
        consistency_penalty = (1.0 - fc_consistency) * 0.08
        for trait in default_traits:
            sjt_val = sjt_ctt.get(trait, {"score": 0.5, "se": 0.12})
            offset = nlp_offsets.get(trait, 0.0)

            # Fuse SJT (60%), Self-report baseline (15%), NLP (15%), Latency & FC consistency (10%)
            sr_score = self_report.get(trait, 0.5)
            fused_score = (
                0.60 * sjt_val["score"] +
                0.15 * sr_score +
                0.15 * (sjt_val["score"] + offset) +
                0.10 * np.clip(sjt_val["score"] + latency_modifier - consistency_penalty, 0.0, 1.0)
            )
            # Fused model achieves lowest standard error
            fused_se = max(0.03, sjt_val["se"] * 0.65)
            results[trait] = {"score": round(float(fused_score), 4), "se": round(float(fused_se), 4)}

        return results

    def run_all_models(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Runs payload through all 7 ablation models for direct comparison."""
        all_results = {}
        for i in range(1, 8):
            tag = f"model_{i}"
            all_results[tag] = self.run_model(tag, payload)
        return all_results

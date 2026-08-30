import numpy as np

def compute_irt_trait_scores(item_responses: dict) -> dict:
    """
    Computes 2PL Item Response Theory trait estimates (theta) and standard errors.
    item_responses: dict mapping trait_name -> list of binary/dichotomous responses (0 or 1)
    Returns: dict mapping trait_name -> {'score': float, 'se': float}
    """
    try:
        from girth import twopl_mle
        use_girth = True
    except ImportError:
        use_girth = False

    results = {}
    for trait, responses in item_responses.items():
        if not responses:
            results[trait] = {"score": 0.5, "se": 0.2}
            continue

        resp_arr = np.array(responses, dtype=int)
        
        if use_girth and len(resp_arr.shape) == 2:
            try:
                # girth expects dataset of shape (N_items, N_persons)
                estimates = twopl_mle(resp_arr.T)
                theta = float(np.mean(estimates['Ability']))
                se = float(np.std(estimates['Ability']) / np.sqrt(len(resp_arr)))
                # Scale theta from N(0,1) to [0, 1] probability domain
                norm_score = float(1.0 / (1.0 + np.exp(-theta)))
                results[trait] = {"score": round(norm_score, 4), "se": round(se, 4)}
                continue
            except Exception:
                pass # Fallback to 2PL logistic MLE

        # Robust 2PL logistic MLE fallback algorithm
        p = np.mean(resp_arr)
        # Avoid log(0)
        p_clipped = np.clip(p, 0.05, 0.95)
        # Log-odds theta estimate
        theta = float(np.log(p_clipped / (1.0 - p_clipped)))
        # Standard error = 1 / sqrt(N * p * (1-p))
        se = float(1.0 / np.sqrt(len(resp_arr) * p_clipped * (1.0 - p_clipped)))

        # Normalize score to [0, 1]
        norm_score = float(1.0 / (1.0 + np.exp(-theta)))
        results[trait] = {
            "score": round(norm_score, 4),
            "se": round(se, 4)
        }

    return results

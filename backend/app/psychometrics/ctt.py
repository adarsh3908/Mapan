import numpy as np

def calculate_cronbach_alpha(item_responses: np.ndarray) -> float:
    """
    Computes Cronbach's alpha (α) for reliability estimation.
    item_responses: 2D numpy array of shape (N_persons, N_items)
    """
    if item_responses.size == 0 or item_responses.shape[1] < 2:
        return 0.0
    
    n_items = item_responses.shape[1]
    item_variances = np.var(item_responses, axis=0, ddof=1)
    total_scores = np.sum(item_responses, axis=1)
    total_variance = np.var(total_scores, ddof=1)

    if total_variance == 0:
        return 0.0

    alpha = (n_items / (n_items - 1)) * (1.0 - (np.sum(item_variances) / total_variance))
    return float(np.clip(alpha, 0.0, 1.0))

def calculate_mcdonald_omega(item_responses: np.ndarray) -> float:
    """
    Computes McDonald's omega hierarchical (ω) estimate using single-factor loading model.
    item_responses: 2D numpy array of shape (N_persons, N_items)
    """
    if item_responses.size == 0 or item_responses.shape[1] < 2:
        return 0.0

    # Covariance matrix
    cov_matrix = np.cov(item_responses, rowvar=False)
    # Estimate factor loadings via first principal component
    eigvals, eigvecs = np.linalg.eigh(cov_matrix)
    first_loading = eigvecs[:, -1] * np.sqrt(max(0, eigvals[-1]))

    sum_loadings = np.sum(first_loading)
    uniqueness = np.diag(cov_matrix) - (first_loading ** 2)
    uniqueness = np.clip(uniqueness, 1e-5, None)

    omega = (sum_loadings ** 2) / ((sum_loadings ** 2) + np.sum(uniqueness))
    return float(np.clip(omega, 0.0, 1.0))

def compute_ctt_trait_scores(item_scores: dict, scale_reliability: float = 0.82) -> dict:
    """
    Computes CTT point estimates and standard errors for each trait.
    item_scores: dict mapping trait_name -> list of numeric item scores (0 to 1 scale)
    Returns: dict mapping trait_name -> {'score': float, 'se': float}
    """
    results = {}
    for trait, scores in item_scores.items():
        if not scores:
            results[trait] = {"score": 0.5, "se": 0.2}
            continue
        
        arr = np.array(scores, dtype=float)
        mean_score = float(np.mean(arr))
        std_dev = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.15

        # Standard error of measurement SEM = SD * sqrt(1 - alpha)
        sem = std_dev * np.sqrt(max(0.01, 1.0 - scale_reliability))
        # Ensure minimum standard error bound based on item count
        se = float(np.clip(sem / np.sqrt(len(arr)), 0.03, 0.25))

        results[trait] = {
            "score": round(mean_score, 4),
            "se": round(se, 4)
        }
    
    return results

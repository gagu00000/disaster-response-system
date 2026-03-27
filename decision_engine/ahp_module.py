"""
AHP (Analytic Hierarchy Process) Module
Implements pairwise comparison matrix construction, eigenvector computation,
consistency checking, and criteria weight derivation per Section 4.2.
"""
import numpy as np


class AHPModule:
    """
    Implements the Analytic Hierarchy Process for multi-criteria decision making.
    Each agent uses this to compute criteria weights from pairwise comparisons.
    """

    CRITERIA = ["speed", "fairness", "cost", "resilience"]
    RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}

    @staticmethod
    def create_comparison_matrix(weights: dict) -> np.ndarray:
        """
        Construct a pairwise comparison matrix from criteria weights.
        Uses Saaty's 1-9 scale. The ratio of weights approximates
        the pairwise comparisons.

        Args:
            weights: dict with keys 'speed', 'fairness', 'cost', 'resilience'
        Returns:
            4x4 pairwise comparison matrix
        """
        criteria = AHPModule.CRITERIA
        n = len(criteria)
        matrix = np.ones((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                wi = max(weights[criteria[i]], 1e-9)
                wj = max(weights[criteria[j]], 1e-9)
                ratio = wi / wj
                # Map ratio to Saaty scale (1-9) using log-based mapping
                if ratio >= 1:
                    saaty_val = 1 + (ratio - 1) * 2
                    saaty_val = min(9, max(1, round(saaty_val)))
                else:
                    inv_ratio = wj / wi
                    saaty_val_inv = 1 + (inv_ratio - 1) * 2
                    saaty_val_inv = min(9, max(1, round(saaty_val_inv)))
                    saaty_val = 1.0 / saaty_val_inv
                matrix[i][j] = saaty_val
                matrix[j][i] = 1.0 / saaty_val

        return matrix

    @staticmethod
    def compute_eigenvector(matrix: np.ndarray) -> np.ndarray:
        """
        Compute the principal eigenvector and normalize to get criteria weights.
        Uses the power method for numerical stability.
        """
        n = matrix.shape[0]
        # Power method
        v = np.ones(n)
        for _ in range(100):
            v_new = matrix @ v
            v_new = v_new / np.sum(v_new)
            if np.allclose(v, v_new, atol=1e-8):
                break
            v = v_new
        return v_new

    @staticmethod
    def compute_consistency_ratio(matrix: np.ndarray, weights: np.ndarray) -> float:
        """
        Compute the Consistency Ratio (CR).
        CR < 0.10 indicates acceptable consistency.
        """
        n = matrix.shape[0]
        if n <= 2:
            return 0.0

        # Compute lambda_max
        weighted_sum = matrix @ weights
        lambda_values = weighted_sum / weights
        lambda_max = np.mean(lambda_values)

        # Consistency Index
        ci = (lambda_max - n) / (n - 1)

        # Random Index
        ri = AHPModule.RANDOM_INDEX.get(n, 1.0)
        if ri == 0:
            return 0.0

        cr = ci / ri
        return round(max(0, cr), 4)

    @staticmethod
    def compute_weights(weight_profile: dict) -> dict:
        """
        Full AHP pipeline: construct matrix, compute eigenvector, check consistency.

        Args:
            weight_profile: dict like {'speed': 0.50, 'fairness': 0.10, 'cost': 0.10, 'resilience': 0.30}

        Returns:
            dict with 'weights', 'consistency_ratio', 'is_consistent', 'comparison_matrix'
        """
        matrix = AHPModule.create_comparison_matrix(weight_profile)
        eigenvector = AHPModule.compute_eigenvector(matrix)
        cr = AHPModule.compute_consistency_ratio(matrix, eigenvector)

        # If inconsistent, use the original normalized weights as fallback
        if cr > 0.10:
            total = sum(weight_profile.values())
            normalized = {k: v / total for k, v in weight_profile.items()}
            weights_array = np.array([normalized[c] for c in AHPModule.CRITERIA])
        else:
            weights_array = eigenvector

        weight_dict = {AHPModule.CRITERIA[i]: round(float(weights_array[i]), 4) for i in range(len(AHPModule.CRITERIA))}

        return {
            "weights": weight_dict,
            "consistency_ratio": cr,
            "is_consistent": cr <= 0.10,
            "comparison_matrix": matrix.tolist()
        }

    @staticmethod
    def score_alternatives(zone_scores: dict, weights: dict) -> dict:
        """
        Score zones by combining fuzzy criterion scores with AHP weights.
        zone_scores: {zone_name: {criterion: score, ...}, ...}
        weights: {criterion: weight, ...}

        Returns: {zone_name: composite_score, ...}
        """
        composite = {}
        for zone_name, scores in zone_scores.items():
            total = 0.0
            for criterion in AHPModule.CRITERIA:
                total += scores.get(criterion, 0.0) * weights.get(criterion, 0.25)
            composite[zone_name] = round(total, 4)
        return composite

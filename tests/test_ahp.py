"""
Test AHP Module
Unit tests for the Analytic Hierarchy Process computation.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.ahp_module import AHPModule


def test_ahp_basic_weights():
    """Test AHP with known weight profile."""
    weights = {"speed": 0.50, "fairness": 0.10, "cost": 0.10, "resilience": 0.30}
    result = AHPModule.compute_weights(weights)
    assert result["is_consistent"], f"AHP should be consistent, CR={result['consistency_ratio']}"
    assert abs(sum(result["weights"].values()) - 1.0) < 0.01, "Weights should sum to 1.0"
    print("  ✅ test_ahp_basic_weights PASSED")


def test_ahp_equal_weights():
    """Test AHP with equal weight profile."""
    weights = {"speed": 0.25, "fairness": 0.25, "cost": 0.25, "resilience": 0.25}
    result = AHPModule.compute_weights(weights)
    assert result["is_consistent"], "Equal weights should be consistent"
    for w in result["weights"].values():
        assert abs(w - 0.25) < 0.05, f"Each weight should be ~0.25, got {w}"
    print("  ✅ test_ahp_equal_weights PASSED")


def test_ahp_all_agent_profiles():
    """Test AHP with all agent weight profiles from the implementation plan."""
    profiles = {
        "Emergency": {"speed": 0.50, "fairness": 0.10, "cost": 0.10, "resilience": 0.30},
        "Government": {"speed": 0.20, "fairness": 0.20, "cost": 0.35, "resilience": 0.25},
        "NGO": {"speed": 0.15, "fairness": 0.45, "cost": 0.10, "resilience": 0.30},
        "AI_Phase1": {"speed": 0.45, "fairness": 0.20, "cost": 0.10, "resilience": 0.25},
        "AI_Phase2": {"speed": 0.25, "fairness": 0.30, "cost": 0.20, "resilience": 0.25},
        "AI_Phase3": {"speed": 0.10, "fairness": 0.25, "cost": 0.30, "resilience": 0.35},
    }
    for name, weights in profiles.items():
        result = AHPModule.compute_weights(weights)
        assert result["is_consistent"], f"{name} profile should be consistent (CR={result['consistency_ratio']})"
        assert abs(sum(result["weights"].values()) - 1.0) < 0.01
    print("  ✅ test_ahp_all_agent_profiles PASSED")


def test_ahp_consistency_ratio():
    """Test that consistency ratio is below threshold."""
    weights = {"speed": 0.50, "fairness": 0.10, "cost": 0.10, "resilience": 0.30}
    result = AHPModule.compute_weights(weights)
    assert result["consistency_ratio"] < 0.10, f"CR should be < 0.10, got {result['consistency_ratio']}"
    print("  ✅ test_ahp_consistency_ratio PASSED")


if __name__ == "__main__":
    print("\n[TEST] AHP Module")
    test_ahp_basic_weights()
    test_ahp_equal_weights()
    test_ahp_all_agent_profiles()
    test_ahp_consistency_ratio()
    print("  ALL AHP TESTS PASSED ✅\n")

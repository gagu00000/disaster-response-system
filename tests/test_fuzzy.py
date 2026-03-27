"""
Test Fuzzy Logic Module
Unit tests for the fuzzy inference system.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.fuzzy_module import FuzzyModule


def test_fuzzy_high_severity():
    """High severity + dense population + difficult access → Very High priority."""
    fuzzy = FuzzyModule()
    score = fuzzy.compute_priority(severity=9.0, population_density=8.0, accessibility=2.0, resource_availability=2.0)
    assert score > 70, f"Expected high priority (>70), got {score}"
    print(f"  ✅ test_fuzzy_high_severity PASSED (score={score:.1f})")


def test_fuzzy_low_severity():
    """Low severity + sparse population + easy access → Low priority."""
    fuzzy = FuzzyModule()
    score = fuzzy.compute_priority(severity=2.0, population_density=2.0, accessibility=8.0, resource_availability=8.0)
    assert score < 40, f"Expected low priority (<40), got {score}"
    print(f"  ✅ test_fuzzy_low_severity PASSED (score={score:.1f})")


def test_fuzzy_moderate_case():
    """Moderate inputs → Medium priority."""
    fuzzy = FuzzyModule()
    score = fuzzy.compute_priority(severity=5.0, population_density=5.0, accessibility=5.0, resource_availability=5.0)
    assert 30 < score < 70, f"Expected medium priority (30-70), got {score}"
    print(f"  ✅ test_fuzzy_moderate_case PASSED (score={score:.1f})")


def test_fuzzy_boundary_values():
    """Test boundary inputs (0 and 10)."""
    fuzzy = FuzzyModule()
    # Maximum severity
    score_max = fuzzy.compute_priority(severity=9.9, population_density=9.9, accessibility=0.1, resource_availability=0.1)
    assert score_max > 60, f"Max inputs should give high priority, got {score_max}"
    # Minimum severity
    score_min = fuzzy.compute_priority(severity=0.1, population_density=0.1, accessibility=9.9, resource_availability=9.9)
    assert score_min < 40, f"Min inputs should give low priority, got {score_min}"
    print(f"  ✅ test_fuzzy_boundary_values PASSED (max={score_max:.1f}, min={score_min:.1f})")


def test_fuzzy_monotonicity():
    """Higher severity should generally produce higher priority."""
    fuzzy = FuzzyModule()
    score_low = fuzzy.compute_priority(severity=2.0, population_density=5.0, accessibility=5.0, resource_availability=5.0)
    score_high = fuzzy.compute_priority(severity=9.0, population_density=5.0, accessibility=5.0, resource_availability=5.0)
    assert score_high > score_low, f"Higher severity should give higher priority: {score_high} vs {score_low}"
    print(f"  ✅ test_fuzzy_monotonicity PASSED (low_sev={score_low:.1f}, high_sev={score_high:.1f})")


if __name__ == "__main__":
    print("\n[TEST] Fuzzy Logic Module")
    test_fuzzy_high_severity()
    test_fuzzy_low_severity()
    test_fuzzy_moderate_case()
    test_fuzzy_boundary_values()
    test_fuzzy_monotonicity()
    print("  ALL FUZZY TESTS PASSED ✅\n")

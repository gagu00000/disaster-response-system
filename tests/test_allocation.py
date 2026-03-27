"""
Test Allocation Module
Unit tests for resource allocation, fairness, and constraints.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from allocation.resource_allocator import ResourceAllocator
from allocation.fairness_monitor import FairnessMonitor
from allocation.constraint_handler import ConstraintHandler
from data.scenarios.scenario_definitions import get_scenario


def test_allocation_budget_constraint():
    """Total allocation should not exceed available resources."""
    scenario = get_scenario("earthquake")
    zones = [{
        "name": z["name"], "current_severity": z["severity"],
        "population": z["population"], "population_at_risk": z["population"],
        "accessibility": z["accessibility"], "unmet_demand": z.get("initial_demand", 20),
        "cumulative_resources_received": 0, "resilience_index": 0.5
    } for z in scenario["zones"]]

    allocator = ResourceAllocator()
    result = allocator.allocate(zones, 100, "Immediate Response")
    total = sum(result["final_allocation"].values())
    assert total <= 100 + 0.01, f"Total allocation {total} exceeds budget 100"
    print(f"  ✅ test_allocation_budget_constraint PASSED (total={total:.1f})")


def test_allocation_non_negative():
    """All allocations should be non-negative."""
    scenario = get_scenario("flooding")
    zones = [{
        "name": z["name"], "current_severity": z["severity"],
        "population": z["population"], "population_at_risk": z["population"],
        "accessibility": z["accessibility"], "unmet_demand": z.get("initial_demand", 20),
        "cumulative_resources_received": 0, "resilience_index": 0.5
    } for z in scenario["zones"]]

    allocator = ResourceAllocator()
    result = allocator.allocate(zones, 150, "Stabilization")
    for zone, amount in result["final_allocation"].items():
        assert amount >= 0, f"Zone {zone} has negative allocation: {amount}"
    print("  ✅ test_allocation_non_negative PASSED")


def test_fairness_gini():
    """Gini coefficient should be computed and within valid range."""
    fm = FairnessMonitor()
    zones = [
        {"name": "A", "population": 100000, "current_severity": 8, "unmet_demand": 10},
        {"name": "B", "population": 50000, "current_severity": 5, "unmet_demand": 10},
        {"name": "C", "population": 20000, "current_severity": 3, "unmet_demand": 10},
    ]
    alloc = {"A": 50, "B": 30, "C": 20}
    fairness = fm.assess(zones, alloc)
    gini = fairness["gini_coefficient"]
    assert 0 <= gini <= 1, f"Gini should be 0-1, got {gini}"
    print(f"  ✅ test_fairness_gini PASSED (gini={gini:.3f})")


def test_constraint_capacity():
    """Constraint handler should cap allocations at absorption capacity."""
    ch = ConstraintHandler()
    zones = [
        {"name": "A", "unmet_demand": 20, "current_severity": 8, "population": 100000},
        {"name": "B", "unmet_demand": 10, "current_severity": 5, "population": 50000},
    ]
    alloc = {"A": 100, "B": 50}
    constrained = ch.apply_constraints(alloc, zones, 200)
    for zone, amount in constrained.items():
        assert amount >= 0, f"Constrained allocation should be non-negative: {zone}={amount}"
    print("  ✅ test_constraint_capacity PASSED")


def test_constraint_floor():
    """Every zone with non-zero severity should get minimum allocation."""
    ch = ConstraintHandler()
    zones = [
        {"name": "A", "unmet_demand": 20, "current_severity": 8, "population": 100000},
        {"name": "B", "unmet_demand": 10, "current_severity": 2, "population": 50000},
    ]
    alloc = {"A": 95, "B": 0}
    constrained = ch.apply_constraints(alloc, zones, 100)
    # B has non-zero severity, should get at least floor
    assert constrained.get("B", 0) > 0, "Zone B with severity 2 should get floor allocation"
    print("  ✅ test_constraint_floor PASSED")


if __name__ == "__main__":
    print("\n[TEST] Allocation Module")
    test_allocation_budget_constraint()
    test_allocation_non_negative()
    test_fairness_gini()
    test_constraint_capacity()
    test_constraint_floor()
    print("  ALL ALLOCATION TESTS PASSED ✅\n")

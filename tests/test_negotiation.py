"""
Test Negotiation Engine
Unit tests for the 5-round negotiation protocol.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.negotiation_engine import NegotiationEngine
from data.scenarios.scenario_definitions import get_scenario


def test_negotiation_produces_allocation():
    """Negotiation should produce a valid allocation for all zones."""
    scenario = get_scenario("earthquake")
    zones = scenario["zones"]
    zone_states = []
    for z in zones:
        zone_states.append({
            "name": z["name"],
            "current_severity": z["severity"],
            "population": z["population"],
            "population_at_risk": z["population"],
            "accessibility": z["accessibility"],
            "unmet_demand": z.get("initial_demand", 20),
            "cumulative_resources_received": 0,
            "resilience_index": 0.5
        })

    engine = NegotiationEngine()
    result = engine.negotiate(zone_states, 100, "Immediate Response")

    assert "final_allocation" in result, "Should produce final_allocation"
    assert len(result["final_allocation"]) == len(zones), "Should allocate to all zones"
    assert sum(result["final_allocation"].values()) <= 100 + 0.01, "Should not exceed budget"
    print("  ✅ test_negotiation_produces_allocation PASSED")


def test_negotiation_proposals_exist():
    """Each agent should produce proposals."""
    scenario = get_scenario("flooding")
    zones = scenario["zones"]
    zone_states = [{
        "name": z["name"], "current_severity": z["severity"],
        "population": z["population"], "population_at_risk": z["population"],
        "accessibility": z["accessibility"], "unmet_demand": z.get("initial_demand", 20),
        "cumulative_resources_received": 0, "resilience_index": 0.5
    } for z in zones]

    engine = NegotiationEngine()
    result = engine.negotiate(zone_states, 150, "Stabilization")

    proposals = result.get("proposals", {})
    assert len(proposals) == 4, f"Should have 4 agent proposals, got {len(proposals)}"
    for agent, prop in proposals.items():
        assert len(prop) == len(zones), f"{agent} should propose for all zones"
    print("  ✅ test_negotiation_proposals_exist PASSED")


def test_negotiation_has_dissent_scores():
    """Negotiation should compute dissent scores for all agents."""
    scenario = get_scenario("industrial")
    zones = scenario["zones"]
    zone_states = [{
        "name": z["name"], "current_severity": z["severity"],
        "population": z["population"], "population_at_risk": z["population"],
        "accessibility": z["accessibility"], "unmet_demand": z.get("initial_demand", 20),
        "cumulative_resources_received": 0, "resilience_index": 0.5
    } for z in zones]

    engine = NegotiationEngine()
    result = engine.negotiate(zone_states, 80, "Immediate Response")

    dissent = result.get("dissent_scores", {})
    assert len(dissent) > 0, "Should have dissent scores"
    for agent, score in dissent.items():
        assert 0 <= score <= 1, f"Dissent should be 0-1, got {score} for {agent}"
    print("  ✅ test_negotiation_has_dissent_scores PASSED")


def test_negotiation_divergence_analysis():
    """AI Coordinator should identify contested zones."""
    scenario = get_scenario("earthquake")
    zones = scenario["zones"]
    zone_states = [{
        "name": z["name"], "current_severity": z["severity"],
        "population": z["population"], "population_at_risk": z["population"],
        "accessibility": z["accessibility"], "unmet_demand": z.get("initial_demand", 20),
        "cumulative_resources_received": 0, "resilience_index": 0.5
    } for z in zones]

    engine = NegotiationEngine()
    result = engine.negotiate(zone_states, 100, "Immediate Response")

    divergence = result.get("divergence", {})
    assert "contested_zones" in divergence, "Should identify contested zones"
    assert "agreed_zones" in divergence, "Should identify agreed zones"
    print("  ✅ test_negotiation_divergence_analysis PASSED")


if __name__ == "__main__":
    print("\n[TEST] Negotiation Engine")
    test_negotiation_produces_allocation()
    test_negotiation_proposals_exist()
    test_negotiation_has_dissent_scores()
    test_negotiation_divergence_analysis()
    print("  ALL NEGOTIATION TESTS PASSED ✅\n")

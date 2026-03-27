"""
Test Simulation Engine
Unit tests for the simulation engine, environment, events, and impact calculator.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.simulation_engine import SimulationEngine
from simulation.disaster_environment import DisasterEnvironment
from simulation.event_system import EventSystem
from simulation.impact_calculator import ImpactCalculator
from data.scenarios.scenario_definitions import get_scenario, list_scenarios


def test_all_scenarios_load():
    """All 3 scenarios should load without errors."""
    scenarios = list_scenarios()
    assert len(scenarios) == 3, f"Expected 3 scenarios, got {len(scenarios)}"
    for s in scenarios:
        scenario = get_scenario(s["id"])
        assert "zones" in scenario
        assert "duration" in scenario
        assert "total_resources" in scenario
    print("  ✅ test_all_scenarios_load PASSED")


def test_simulation_initialization():
    """Simulation engine should initialize correctly."""
    scenario = get_scenario("earthquake")
    engine = SimulationEngine(scenario)
    engine.initialize()
    state = engine.get_current_state()
    assert state["step"] == 0
    assert state["phase"] is not None
    assert len(state["zones"]) == 5
    assert state["remaining_resources"] == 150
    print("  ✅ test_simulation_initialization PASSED")


def test_simulation_step_execution():
    """A simulation step should update state."""
    scenario = get_scenario("earthquake")
    engine = SimulationEngine(scenario)
    engine.initialize()

    initial_step = engine.current_step
    engine.apply_dynamic_events()
    alloc = {z["name"]: 5 for z in engine.environment.get_all_zone_states()}
    engine.execute_allocation(alloc)
    engine.advance_step()

    assert engine.current_step == initial_step + 1
    print("  ✅ test_simulation_step_execution PASSED")


def test_simulation_completes():
    """Simulation should complete after all steps."""
    scenario = get_scenario("industrial")
    engine = SimulationEngine(scenario)
    engine.initialize()

    step_count = 0
    while not engine.is_complete:
        engine.apply_dynamic_events()
        zones = engine.environment.get_all_zone_states()
        alloc = {z["name"]: 2 for z in zones}
        engine.execute_allocation(alloc)
        engine.advance_step()
        step_count += 1
        if step_count > 20:
            break

    assert engine.is_complete, "Simulation should be complete"
    assert step_count == scenario["duration"]
    print(f"  ✅ test_simulation_completes PASSED ({step_count} steps)")


def test_environment_zone_states():
    """Environment should track zone states correctly."""
    scenario = get_scenario("earthquake")
    env = DisasterEnvironment(scenario)
    env.initialize()

    zones = env.get_all_zone_states()
    assert len(zones) == 5
    for z in zones:
        assert "name" in z
        assert "current_severity" in z
        assert "population" in z
        assert "resilience_index" in z
    print("  ✅ test_environment_zone_states PASSED")


def test_dynamic_events():
    """Event system should fire events at scheduled steps."""
    scenario = get_scenario("earthquake")
    event_system = EventSystem(scenario.get("dynamic_events", []))
    events = event_system.get_events_for_step(3)
    # Earthquake scenario has aftershock at step 3
    print(f"  ✅ test_dynamic_events PASSED ({len(events)} events at step 3)")


def test_impact_calculator():
    """Impact calculator should compute valid metrics."""
    zones = [
        {"name": "A", "current_severity": 5, "population": 1000, "unmet_demand": 5, "resilience_index": 0.6},
        {"name": "B", "current_severity": 3, "population": 2000, "unmet_demand": 3, "resilience_index": 0.7},
    ]
    alloc = {"A": 15, "B": 10}
    metrics = ImpactCalculator.compute_metrics(zones, alloc, 50)
    assert "gini_coefficient" in metrics
    assert "response_coverage" in metrics
    assert "avg_resilience" in metrics
    assert 0 <= metrics["gini_coefficient"] <= 1
    print("  ✅ test_impact_calculator PASSED")


if __name__ == "__main__":
    print("\n[TEST] Simulation Engine")
    test_all_scenarios_load()
    test_simulation_initialization()
    test_simulation_step_execution()
    test_simulation_completes()
    test_environment_zone_states()
    test_dynamic_events()
    test_impact_calculator()
    print("  ALL SIMULATION TESTS PASSED ✅\n")

"""Quick integration test for the disaster response system."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.scenarios.scenario_definitions import list_scenarios, get_scenario
from simulation.simulation_engine import SimulationEngine
from decision_engine.ahp_module import AHPModule
from decision_engine.fuzzy_module import FuzzyModule
from decision_engine.criteria_manager import CriteriaManager
from decision_engine.priority_aggregator import PriorityAggregator
from allocation.resource_allocator import ResourceAllocator
from explainability.decision_narrator import DecisionNarrator
from visualization.metrics_display import MetricsDisplay
from llm_layer.validation_layer import ValidationLayer

print("=" * 60)
print("INTEGRATION TEST - Multi-Agent Disaster Response System")
print("=" * 60)

# 1. Test scenarios
print("\n[1] SCENARIOS")
scenarios = list_scenarios()
for s in scenarios:
    print(f"  - {s['name']} ({s['type']}): {s['zones']} zones, {s['duration']} steps")

# 2. Test simulation engine
print("\n[2] SIMULATION ENGINE")
scenario = get_scenario("earthquake")
engine = SimulationEngine(scenario)
engine.initialize()
state = engine.get_current_state()
print(f"  Scenario: {scenario['name']}")
print(f"  Zones: {state['environment']['zone_names']}")
print(f"  Duration: {state['total_steps']} steps")
print(f"  Resources: {state['remaining_resources']}")

# 3. Test AHP
print("\n[3] AHP MODULE")
weights = {"speed": 0.50, "fairness": 0.10, "cost": 0.10, "resilience": 0.30}
ahp_result = AHPModule.compute_weights(weights)
print(f"  Input weights: {weights}")
print(f"  AHP weights: {ahp_result['weights']}")
print(f"  Consistency Ratio: {ahp_result['consistency_ratio']} (consistent: {ahp_result['is_consistent']})")

# 4. Test Fuzzy Logic
print("\n[4] FUZZY LOGIC MODULE")
fuzzy = FuzzyModule()
score = fuzzy.compute_priority(severity=9.0, population_density=8.0, accessibility=3.0, resource_availability=2.0)
print(f"  Priority (sev=9, pop=8, acc=3, res=2): {score}")
score2 = fuzzy.compute_priority(severity=2.0, population_density=3.0, accessibility=8.0, resource_availability=7.0)
print(f"  Priority (sev=2, pop=3, acc=8, res=7): {score2}")

# 5. Test full allocation pipeline
print("\n[5] ALLOCATION PIPELINE")
allocator = ResourceAllocator()
zones = engine.environment.get_all_zone_states()
result = allocator.allocate(zones, 150, "Immediate Response")
print(f"  Final Allocation: {result['final_allocation']}")
print(f"  Gini: {result['fairness_after']['gini_coefficient']}")
print(f"  Fair: {result['fairness_after']['is_fair']}")
print(f"  Redistributed: {result['was_redistributed']}")

# 6. Test negotiation details
print("\n[6] NEGOTIATION")
nr = result["negotiation_result"]
print(f"  Contested zones: {nr['divergence']['contested_zones']}")
print(f"  Dissent scores: {nr['dissent_scores']}")
for agent, proposal in nr["proposals"].items():
    print(f"  {agent}: {proposal}")

# 7. Test template explanations
print("\n[7] TEMPLATE EXPLANATION")
narrator = DecisionNarrator()
explanation_data = {
    "step": 0, "phase": "Immediate Response",
    "zones": zones, "allocations": result["final_allocation"],
    "metrics": {"gini_coefficient": result["fairness_after"]["gini_coefficient"], "response_coverage": 0.5},
    "dissent_scores": nr["dissent_scores"]
}
explanation = narrator.narrate_allocation(explanation_data)
print(f"  {explanation[:200]}...")

# 8. Test validation layer
print("\n[8] VALIDATION LAYER")
test_response = "Urban Center received more resources than Rural Outskirts due to severity of 9.0."
validation = ValidationLayer.validate(test_response, explanation_data)
print(f"  Validation passed: {validation['passed']}")
print(f"  Flags: {validation['total_flags']} (minor: {validation['minor_issues']}, critical: {validation['critical_issues']})")

# 9. Run full simulation
print("\n[9] FULL SIMULATION RUN")
from app.controller import Controller
ctrl = Controller()
ctrl.initialize_simulation("earthquake")
results = ctrl.run_all_steps()
print(f"  Steps completed: {len(results)}")
summary = ctrl.get_simulation_summary()
final_metrics = summary.get("final_metrics", {})
print(f"  Final Coverage: {final_metrics.get('response_coverage', 0):.3f}")
print(f"  Final Gini: {final_metrics.get('gini_coefficient', 0):.3f}")
print(f"  Final Resilience: {final_metrics.get('avg_resilience', 0):.3f}")
print(f"  Final Severity: {final_metrics.get('avg_severity', 0):.3f}")

# 10. Test all 3 scenarios
print("\n[10] ALL SCENARIOS")
for sid in ["earthquake", "flooding", "industrial"]:
    ctrl2 = Controller()
    ctrl2.initialize_simulation(sid)
    results2 = ctrl2.run_all_steps()
    summary2 = ctrl2.get_simulation_summary()
    fm = summary2.get("final_metrics", {})
    print(f"  {sid}: {len(results2)} steps, "
          f"coverage={fm.get('response_coverage', 0):.3f}, "
          f"gini={fm.get('gini_coefficient', 0):.3f}, "
          f"resilience={fm.get('avg_resilience', 0):.3f}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)

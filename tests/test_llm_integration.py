"""
Test LLM Integration
Unit tests for prompt engine, validation layer, and response formatting.
Runs without Ollama — tests structural components only.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_layer.prompt_engine import PromptEngine
from llm_layer.validation_layer import ValidationLayer
from llm_layer.response_formatter import ResponseFormatter
from llm_layer.llm_cache import LLMCache
from llm_layer.llm_client import LLMClient


def test_prompt_explanation():
    """Decision explanation prompt should contain structured data."""
    step_data = {
        "step": 3, "phase": "Immediate Response",
        "zones": [{"name": "Zone A", "current_severity": 8.5, "population": 50000,
                    "population_at_risk": 50000, "accessibility": 3.0, "unmet_demand": 15}],
        "allocations": {"Zone A": 35},
        "metrics": {"response_coverage": 0.78, "gini_coefficient": 0.22, "total_cost": 35, "avg_resilience": 0.6},
        "dissent_scores": {"Emergency Response": 0.05}
    }
    prompt = PromptEngine.build_explanation_prompt(step_data)
    assert "Zone A" in prompt, "Prompt should contain zone name"
    assert "8.5" in prompt, "Prompt should contain severity"
    assert "Immediate Response" in prompt, "Prompt should contain phase"
    print("  ✅ test_prompt_explanation PASSED")


def test_prompt_query():
    """Query prompt should contain user question and simulation state."""
    state = {
        "scenario": {"name": "Earthquake"},
        "total_steps_completed": 10,
        "final_zone_states": [{"name": "A", "current_severity": 5, "population": 1000,
                                "cumulative_resources_received": 50, "unmet_demand": 5}],
        "final_metrics": {"response_coverage": 0.8},
        "allocation_history": []
    }
    prompt = PromptEngine.build_query_prompt("Why did Zone A get more?", state)
    assert "Why did Zone A get more?" in prompt
    assert "Earthquake" in prompt
    print("  ✅ test_prompt_query PASSED")


def test_prompt_insight():
    """Insight prompt should contain metrics and zone data."""
    data = {
        "scenario": {"name": "Earthquake", "type": "earthquake", "duration": 15, "total_resources": 150},
        "metrics_history": [{"step": 0, "response_coverage": 0.7, "gini_coefficient": 0.2, "avg_resilience": 0.6}],
        "final_zone_states": [{"name": "A", "current_severity": 3, "cumulative_resources_received": 50, "resilience_index": 0.7}],
        "allocation_history": []
    }
    prompt = PromptEngine.build_insight_prompt(data)
    assert "Earthquake" in prompt
    assert "REPORT FORMAT" in prompt
    print("  ✅ test_prompt_insight PASSED")


def test_prompt_scenario():
    """Scenario prompt should contain scenario metadata."""
    from data.scenarios.scenario_definitions import get_scenario
    scenario = get_scenario("earthquake")
    prompt = PromptEngine.build_scenario_prompt(scenario)
    assert "earthquake" in prompt.lower()
    assert "Urban Center" in prompt or "5" in prompt
    print("  ✅ test_prompt_scenario PASSED")


def test_validation_clean_response():
    """Clean response should pass validation."""
    response = "Zone A received 35 units due to severity of 8.5 out of 10."
    context = {
        "zones": [{"name": "Zone A", "current_severity": 8.5, "population": 50000}],
        "allocations": {"Zone A": 35},
        "metrics": {"response_coverage": 0.78}
    }
    result = ValidationLayer.validate(response, context)
    assert result["passed"], f"Clean response should pass, flags={result['flags']}"
    print("  ✅ test_validation_clean_response PASSED")


def test_validation_speculative_content():
    """Speculative language should be flagged."""
    response = "Zone A could have received more resources if only there were more available."
    context = {
        "zones": [{"name": "Zone A", "current_severity": 8.5, "population": 50000}],
        "allocations": {"Zone A": 35},
        "metrics": {}
    }
    result = ValidationLayer.validate(response, context)
    assert result["total_flags"] > 0, "Speculative language should be flagged"
    print(f"  ✅ test_validation_speculative_content PASSED ({result['total_flags']} flags)")


def test_validation_external_reference():
    """External references should be critically flagged."""
    response = "According to studies, this allocation is optimal. Historically, similar disasters show this pattern."
    context = {"zones": [], "allocations": {}, "metrics": {}}
    result = ValidationLayer.validate(response, context)
    critical = result["critical_issues"]
    assert critical > 0, "External references should be critical flags"
    print(f"  ✅ test_validation_external_reference PASSED ({critical} critical flags)")


def test_response_formatter():
    """Response formatter should add AI labels."""
    formatted = ResponseFormatter.format_explanation("Zone A received 35 units.")
    assert "AI-Generated" in formatted
    formatted_caveat = ResponseFormatter.format_explanation("Zone A received 35 units.", caveat=True)
    assert "approximate" in formatted_caveat
    print("  ✅ test_response_formatter PASSED")


def test_cache():
    """LLM cache should store and retrieve responses."""
    cache = LLMCache()
    cache.set_explanation("eq", 1, {"A": 10}, "Test explanation")
    result = cache.get_explanation("eq", 1, {"A": 10})
    assert result == "Test explanation"
    cache.clear()
    result2 = cache.get_explanation("eq", 1, {"A": 10})
    assert result2 is None
    print("  ✅ test_cache PASSED")


def test_client_graceful_degradation():
    """LLM client should degrade gracefully when Ollama is unavailable."""
    client = LLMClient()
    # Don't call test_connection — just verify status
    status = client.get_status()
    assert "model" in status
    assert "is_connected" in status
    print("  ✅ test_client_graceful_degradation PASSED")


if __name__ == "__main__":
    print("\n[TEST] LLM Integration")
    test_prompt_explanation()
    test_prompt_query()
    test_prompt_insight()
    test_prompt_scenario()
    test_validation_clean_response()
    test_validation_speculative_content()
    test_validation_external_reference()
    test_response_formatter()
    test_cache()
    test_client_graceful_degradation()
    print("  ALL LLM INTEGRATION TESTS PASSED ✅\n")

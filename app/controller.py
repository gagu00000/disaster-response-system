"""
Application Controller Module
Orchestrates the entire simulation lifecycle: initialization, step execution,
data routing between components, and LLM request routing.
Per Section 2.3 Layer 2.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.scenarios.scenario_definitions import get_scenario, list_scenarios, ALL_SCENARIOS
from simulation.simulation_engine import SimulationEngine
from allocation.resource_allocator import ResourceAllocator
from explainability.decision_narrator import DecisionNarrator
from explainability.tradeoff_reporter import TradeoffReporter
from explainability.audit_trail import AuditTrail


class Controller:
    """
    Application Controller — manages the simulation lifecycle
    and routes data between all system layers.
    """

    def __init__(self):
        self.sim_engine = None
        self.allocator = None
        self.narrator = DecisionNarrator()
        self.tradeoff_reporter = TradeoffReporter()
        self.audit_trail = AuditTrail()
        self.llm_available = False
        self.llm_client = None

        # State
        self.current_scenario_id = None
        self.step_results = []
        self.ai_weight_history = []
        self.is_initialized = False

    def initialize_simulation(self, scenario_id: str):
        """Initialize all components for a given scenario."""
        scenario = get_scenario(scenario_id)
        self.current_scenario_id = scenario_id

        self.sim_engine = SimulationEngine(scenario)
        self.sim_engine.initialize()

        self.allocator = ResourceAllocator()
        self.allocator.reset()

        self.audit_trail = AuditTrail()
        self.step_results = []
        self.ai_weight_history = []
        self.is_initialized = True

        # Try to initialize LLM
        self._init_llm()

        return self.sim_engine.get_current_state()

    def _init_llm(self):
        """Attempt to connect to the LLM layer."""
        try:
            from llm_layer.llm_client import LLMClient
            self.llm_client = LLMClient()
            self.llm_available = self.llm_client.test_connection()
        except Exception:
            self.llm_available = False
            self.llm_client = None

    def run_step(self) -> dict:
        """Execute one complete simulation step."""
        if not self.is_initialized or self.sim_engine.is_complete:
            return {"error": "Simulation not initialized or already complete"}

        # Get current state
        state = self.sim_engine.get_current_state()
        zones = state["zones"]
        phase = state["phase"]
        available = state["remaining_resources"]

        # Apply dynamic events
        events = self.sim_engine.apply_dynamic_events()

        # Run allocation pipeline (negotiation → constraints → fairness → allocation)
        zones_after_events = self.sim_engine.environment.get_all_zone_states()
        allocation_result = self.allocator.allocate(zones_after_events, available, phase)

        # Execute allocation in simulation
        final_alloc = allocation_result["final_allocation"]
        metrics = self.sim_engine.execute_allocation(final_alloc)

        # Track AI Coordinator weight evolution
        agent_states = allocation_result["negotiation_result"].get("agent_states", {})
        if "AI Coordinator" in agent_states:
            self.ai_weight_history.append(agent_states["AI Coordinator"].get("weights", {}))

        # Generate template-based explanation
        explanation_data = {
            "step": state["step"],
            "phase": phase,
            "zones": self.sim_engine.environment.get_all_zone_states(),
            "allocations": final_alloc,
            "metrics": metrics,
            "dissent_scores": allocation_result["negotiation_result"].get("dissent_scores", {})
        }
        template_explanation = self.narrator.narrate_allocation(explanation_data)

        # Analyze trade-offs
        tradeoffs = self.tradeoff_reporter.analyze_tradeoffs(allocation_result, zones_after_events)

        # Log to audit trail
        self.audit_trail.log_allocation(
            step=state["step"],
            allocation=final_alloc,
            metrics=metrics,
            negotiation_summary={
                "contested_zones": allocation_result["negotiation_result"].get("divergence", {}).get("contested_zones", []),
                "dissent_scores": allocation_result["negotiation_result"].get("dissent_scores", {})
            }
        )
        for event in events:
            self.audit_trail.log_event(state["step"], event)

        # Build step result
        step_result = {
            "step": state["step"],
            "phase": phase,
            "events": events,
            "allocation_result": allocation_result,
            "final_allocation": final_alloc,
            "metrics": metrics,
            "template_explanation": template_explanation,
            "tradeoffs": tradeoffs,
            "post_state": self.sim_engine.environment.get_all_zone_states(),
            "remaining_resources": self.sim_engine.environment.remaining_resources
        }
        self.step_results.append(step_result)

        # Advance simulation
        self.sim_engine.advance_step()

        return step_result

    def run_all_steps(self) -> list:
        """Run all remaining simulation steps."""
        results = []
        while not self.sim_engine.is_complete:
            result = self.run_step()
            results.append(result)
        return results

    def get_current_state(self) -> dict:
        """Get the current simulation state."""
        if not self.is_initialized:
            return {"error": "Not initialized"}
        state = self.sim_engine.get_current_state()
        state["llm_available"] = self.llm_available
        return state

    def get_simulation_summary(self) -> dict:
        """Get complete simulation summary for post-simulation analysis."""
        if not self.sim_engine:
            return {}
        summary = self.sim_engine.get_simulation_summary()
        summary["ai_weight_history"] = self.ai_weight_history
        summary["template_summary"] = self.narrator.narrate_summary(summary)
        return summary

    def get_scenario_narration(self, scenario_id: str = None) -> str:
        """Get template-based scenario narration."""
        sid = scenario_id or self.current_scenario_id
        if sid:
            scenario = get_scenario(sid)
            return self.narrator.narrate_scenario(scenario)
        return "No scenario selected."

    def get_llm_explanation(self, step_data: dict) -> str:
        """Get LLM-generated explanation (falls back to template)."""
        if self.llm_available and self.llm_client:
            try:
                from llm_layer.prompt_engine import PromptEngine
                from llm_layer.validation_layer import ValidationLayer
                from llm_layer.response_formatter import ResponseFormatter

                prompt = PromptEngine.build_explanation_prompt(step_data)
                raw_response = self.llm_client.generate(prompt)
                validation = ValidationLayer.validate(raw_response, step_data)

                if validation["passed"]:
                    return ResponseFormatter.format_explanation(raw_response)
                elif validation.get("minor_issues", 0) <= 2:
                    return ResponseFormatter.format_explanation(raw_response, caveat=True)
                else:
                    return step_data.get("template_explanation", "Explanation unavailable.")
            except Exception:
                pass
        return step_data.get("template_explanation", "Explanation unavailable.")

    def get_llm_query_response(self, question: str) -> str:
        """Handle user query via LLM (falls back to message)."""
        if self.llm_available and self.llm_client:
            try:
                from llm_layer.query_handler import QueryHandler
                handler = QueryHandler(self.llm_client)
                summary = self.get_simulation_summary()
                return handler.handle_query(question, summary)
            except Exception:
                pass
        return "AI Query requires Ollama. Please see setup instructions."

    def get_llm_insights(self) -> str:
        """Generate LLM post-simulation insights (falls back to template)."""
        summary = self.get_simulation_summary()
        if self.llm_available and self.llm_client:
            try:
                from llm_layer.insight_generator import InsightGenerator
                generator = InsightGenerator(self.llm_client)
                return generator.generate_report(summary)
            except Exception:
                pass
        return summary.get("template_summary", "Simulation summary unavailable.")

    @staticmethod
    def get_available_scenarios() -> list:
        """Return list of available scenarios."""
        return list_scenarios()

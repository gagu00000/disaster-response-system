"""
Insight Generator Module
Post-simulation analysis report generation using LLM.
Per Section 17.3.
"""
from llm_layer.prompt_engine import PromptEngine
from llm_layer.validation_layer import ValidationLayer
from llm_layer.response_formatter import ResponseFormatter


class InsightGenerator:
    """Generates comprehensive post-simulation insight reports."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_report(self, simulation_data: dict) -> str:
        """
        Generate a comprehensive narrative report from complete simulation data.

        Args:
            simulation_data: complete simulation summary dict

        Returns:
            Formatted insight report string
        """
        try:
            prompt = PromptEngine.build_insight_prompt(simulation_data)
            system_prompt = PromptEngine.get_system_prompt("insight")

            result = self.llm_client.generate_with_timing(
                prompt, system_prompt=system_prompt, max_tokens=800
            )

            if not result["success"]:
                return simulation_data.get("template_summary", "Unable to generate insights.")

            raw_response = result["text"]

            # Validate
            validation = ValidationLayer.validate(raw_response, {
                "zones": simulation_data.get("final_zone_states", []),
                "metrics": simulation_data.get("final_metrics", {}),
                "step": simulation_data.get("total_steps_completed", 0)
            })

            if validation["passed"]:
                formatted = ResponseFormatter.format_insight_report(raw_response)
                return ResponseFormatter.truncate_if_needed(formatted)
            else:
                # Fallback to template
                return simulation_data.get("template_summary", "Unable to generate validated insights.")

        except Exception:
            return simulation_data.get("template_summary", "Insight generation unavailable.")

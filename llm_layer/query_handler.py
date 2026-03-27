"""
Query Handler Module
Processes user questions and generates grounded answers using the LLM.
Per Section 17.2.
"""
from llm_layer.prompt_engine import PromptEngine
from llm_layer.validation_layer import ValidationLayer
from llm_layer.response_formatter import ResponseFormatter


class QueryHandler:
    """Handles user questions about the simulation via LLM."""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def handle_query(self, question: str, simulation_state: dict) -> str:
        """
        Process a user question and return a grounded answer.

        Args:
            question: user's free-text question
            simulation_state: complete simulation state snapshot

        Returns:
            Formatted answer string
        """
        try:
            # Build prompt
            prompt = PromptEngine.build_query_prompt(question, simulation_state)
            system_prompt = PromptEngine.get_system_prompt("query")

            # Generate response
            result = self.llm_client.generate_with_timing(
                prompt, system_prompt=system_prompt, max_tokens=200
            )

            if not result["success"]:
                return "Unable to generate a response. Please try again."

            raw_response = result["text"]

            # Validate
            validation = ValidationLayer.validate(raw_response, simulation_state)

            if validation["passed"]:
                return ResponseFormatter.format_query_response(raw_response)
            else:
                return ("This question cannot be fully answered from the current simulation data. "
                        "Please rephrase or ask about specific zone allocations, metrics, or agent decisions.")

        except Exception as e:
            return f"AI Query requires Ollama. Please see setup instructions. (Error: {str(e)})"

"""
Chatbot Engine — Multi-turn conversational AI grounded in simulation data.
Uses Ollama for local LLM inference with full conversation history.
"""

from llm_layer.llm_client import LLMClient


class ChatbotEngine:
    """
    Multi-turn chatbot that answers questions about the disaster simulation.
    Automatically injects simulation context so the LLM stays data-grounded.
    """

    SYSTEM_PROMPT = (
        "You are ESARS AI Assistant — an expert analyst for a multi-agent disaster "
        "response and resource allocation simulation system.\n\n"
        "YOUR ROLE:\n"
        "- Answer questions about the simulation: zone statuses, resource allocations, "
        "agent decisions, negotiation outcomes, fairness metrics, and trade-offs.\n"
        "- Explain WHY certain decisions were made by referencing specific data.\n"
        "- Compare zones, steps, and agent behaviors when asked.\n\n"
        "STRICT RULES:\n"
        "1. Use ONLY the simulation data provided in the CONTEXT block. "
        "Do NOT use external knowledge about real disasters.\n"
        "2. Reference specific numbers: zone names, severity scores, allocation amounts, "
        "Gini coefficients, coverage percentages.\n"
        "3. If the simulation has not been run yet or the data is insufficient, say so clearly.\n"
        "4. Keep answers concise (3-6 sentences) unless the user asks for detail.\n"
        "5. Use professional, neutral language. No emotional commentary.\n"
        "6. If asked about something unrelated to the simulation, politely redirect: "
        "\"I can only answer questions about the current disaster simulation data.\"\n"
        "7. When comparing or explaining trade-offs, structure your answer clearly.\n"
    )

    MAX_HISTORY = 20  # max conversation turns to send to LLM

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.history = []  # list of {"role": str, "content": str}

    def _build_context_block(self, simulation_state: dict) -> str:
        """Build a compact simulation data context string."""
        if not simulation_state:
            return "CONTEXT:\nNo simulation has been run yet. No data available.\n"

        parts = ["CONTEXT (SIMULATION DATA):"]

        scenario = simulation_state.get("scenario", {})
        if scenario:
            parts.append(
                f"Scenario: {scenario.get('name', '?')} | "
                f"Type: {scenario.get('type', '?')} | "
                f"Steps completed: {simulation_state.get('total_steps_completed', 0)}"
            )

        zones = simulation_state.get("final_zone_states", [])
        if zones:
            parts.append("\nZONE STATUS:")
            for z in zones:
                parts.append(
                    f"  {z['name']}: Severity={z['current_severity']:.1f}/10, "
                    f"Pop={z['population']}, "
                    f"Resources={z['cumulative_resources_received']:.1f}, "
                    f"Unmet={z['unmet_demand']:.1f}, "
                    f"Resilience={z['resilience_index']:.3f}"
                )

        metrics = simulation_state.get("final_metrics", {})
        if metrics:
            parts.append("\nFINAL METRICS:")
            for k, v in metrics.items():
                if isinstance(v, float):
                    parts.append(f"  {k}: {v:.4f}")
                elif isinstance(v, (int,)):
                    parts.append(f"  {k}: {v}")

        alloc_history = simulation_state.get("allocation_history", [])
        if alloc_history:
            parts.append(f"\nALLOCATION HISTORY (last 3 of {len(alloc_history)} steps):")
            for ah in alloc_history[-3:]:
                allocs = ah.get("allocations", {})
                alloc_str = ", ".join(f"{z}={v:.1f}" for z, v in allocs.items())
                parts.append(f"  Step {ah.get('step', '?')}: {alloc_str}")

        metrics_history = simulation_state.get("metrics_history", [])
        if metrics_history:
            parts.append(f"\nMETRICS OVER TIME ({len(metrics_history)} steps):")
            for m in metrics_history:
                parts.append(
                    f"  Step {m.get('step', '?')}: "
                    f"Coverage={m.get('response_coverage', 0):.3f}, "
                    f"Gini={m.get('gini_coefficient', 0):.3f}, "
                    f"Resilience={m.get('avg_resilience', 0):.3f}"
                )

        baselines = simulation_state.get("baselines", {})
        if baselines:
            parts.append("\nBASELINE COMPARISONS (last step):")
            for name, alloc in baselines.items():
                alloc_str = ", ".join(f"{z}={v:.1f}" for z, v in alloc.items())
                parts.append(f"  {name}: {alloc_str}")

        ai_weights = simulation_state.get("ai_weight_history", [])
        if ai_weights:
            parts.append("\nAI COORDINATOR WEIGHT EVOLUTION:")
            for i, w in enumerate(ai_weights):
                w_str = ", ".join(f"{k}={v:.2f}" for k, v in w.items())
                parts.append(f"  Step {i+1}: {w_str}")

        return "\n".join(parts)

    def _get_messages(self, simulation_state: dict) -> list:
        """Build the full messages array for the LLM."""
        context = self._build_context_block(simulation_state)
        system_msg = self.SYSTEM_PROMPT + "\n\n" + context

        messages = [{"role": "system", "content": system_msg}]

        # Trim history to MAX_HISTORY messages
        trimmed = self.history[-self.MAX_HISTORY:]
        messages.extend(trimmed)

        return messages

    def ask(self, question: str, simulation_state: dict) -> str:
        """
        Send a user question and get a grounded response.

        Args:
            question: User's question text
            simulation_state: Current simulation summary dict from controller

        Returns:
            Assistant response string
        """
        self.history.append({"role": "user", "content": question})

        try:
            messages = self._get_messages(simulation_state)
            response = self.llm_client.chat(messages, max_tokens=600, temperature=0.3)
            response = response.strip()
            if not response:
                response = "I couldn't generate a response. Please try rephrasing your question."
        except ConnectionError:
            response = "LLM is not available. Please check that Ollama is running."
        except Exception as e:
            response = f"Error generating response: {str(e)}"

        self.history.append({"role": "assistant", "content": response})
        return response

    def clear_history(self):
        """Clear conversation history."""
        self.history.clear()

    def get_history(self) -> list:
        """Return conversation history for display."""
        return list(self.history)

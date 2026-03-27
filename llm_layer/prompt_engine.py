"""
Prompt Engine Module
Constructs structured prompts for each LLM integration point.
Contains all prompt templates from Section 20.2-20.5.
"""


class PromptEngine:
    """Builds controlled, data-grounded prompts for LLM generation."""

    # --- System prompts ---
    EXPLANATION_SYSTEM = (
        "You are a disaster response analyst. Your role is to explain "
        "resource allocation decisions in clear, factual language.\n\n"
        "STRICT RULES:\n"
        "- Use ONLY the data provided below. Do not add external knowledge.\n"
        "- Reference specific numbers from the data (severity scores, "
        "population counts, allocation amounts).\n"
        "- Do not speculate about what \"could have\" or \"should have\" happened.\n"
        "- Do not express opinions or emotional language.\n"
        "- If data is insufficient to explain something, say "
        "\"Insufficient data available for this aspect.\"\n"
        "- Keep your response to 3-5 sentences."
    )

    QUERY_SYSTEM = (
        "You are a disaster response data analyst. Answer the user's "
        "question using ONLY the simulation data provided below.\n\n"
        "STRICT RULES:\n"
        "- Answer ONLY from the provided data. No external knowledge.\n"
        "- If the question cannot be answered from the data, respond: "
        "\"This question cannot be answered from the current simulation data.\"\n"
        "- Reference specific numbers and zone names.\n"
        "- Keep your answer concise (2-4 sentences).\n"
        "- Do not speculate or hypothesize."
    )

    INSIGHT_SYSTEM = (
        "You are a disaster response analyst writing a post-simulation "
        "assessment report. Analyze the complete simulation data provided "
        "below and generate a structured report.\n\n"
        "STRICT RULES:\n"
        "- Use ONLY the data provided. No external knowledge.\n"
        "- Every claim must reference specific numbers from the data.\n"
        "- Do not speculate about alternative outcomes.\n"
        "- Use neutral, professional language."
    )

    SCENARIO_SYSTEM = (
        "You are a disaster briefing officer providing a situation "
        "overview. Describe the scenario using ONLY the data provided.\n\n"
        "STRICT RULES:\n"
        "- Use ONLY the provided scenario data.\n"
        "- Keep it to 2-3 sentences.\n"
        "- Include the disaster type, number of zones, severity range, "
        "and key challenges.\n"
        "- Use professional, neutral language."
    )

    @staticmethod
    def build_explanation_prompt(step_data: dict) -> str:
        """Build the Decision Explanation prompt (Section 20.2)."""
        zones = step_data.get("zones", step_data.get("post_state", []))
        allocations = step_data.get("allocations", step_data.get("final_allocation", {}))
        metrics = step_data.get("metrics", {})
        step = step_data.get("step", 0)
        phase = step_data.get("phase", "Unknown")
        dissent = step_data.get("dissent_scores", {})

        nr = step_data.get("allocation_result", {}).get("negotiation_result", {})
        proposals = nr.get("proposals", {})
        divergence = nr.get("divergence", {})

        prompt = f"CONTEXT DATA:\nDisaster Phase: {phase}\nCurrent Time Step: {step}\n\n"
        prompt += "ZONE STATUS:\n"
        for z in zones:
            prompt += (
                f"  Zone: {z['name']}\n"
                f"  Severity: {z['current_severity']}/10\n"
                f"  Population at Risk: {z.get('population_at_risk', z['population'])}\n"
                f"  Accessibility: {z['accessibility']}/10\n"
                f"  Resources Received This Step: {allocations.get(z['name'], 0)}\n"
                f"  Unmet Demand: {z['unmet_demand']}\n\n"
            )

        if proposals:
            prompt += "AGENT EVALUATIONS:\n"
            agent_states = nr.get("agent_states", {})
            for agent_type, state in agent_states.items():
                weights = state.get("weights", {})
                ranking = state.get("priorities", {}).get("ranking", [])
                rank_str = ", ".join([f"{r['zone']}({r['score']:.1f})" for r in ranking[:3]])
                prompt += (
                    f"  Agent: {agent_type}\n"
                    f"  Priority Ranking: {rank_str}\n"
                    f"  Criteria Weights: Speed={weights.get('speed',0)}, "
                    f"Fairness={weights.get('fairness',0)}, "
                    f"Cost={weights.get('cost',0)}, "
                    f"Resilience={weights.get('resilience',0)}\n\n"
                )

        if divergence:
            prompt += f"NEGOTIATION OUTCOME:\n"
            prompt += f"  Contested Zones: {', '.join(divergence.get('contested_zones', []))}\n"
            prompt += f"  Final Consensus: {allocations}\n\n"

        prompt += (
            f"PERFORMANCE METRICS:\n"
            f"  Average Coverage: {metrics.get('response_coverage', 0):.1%}\n"
            f"  Gini Coefficient: {metrics.get('gini_coefficient', 0):.3f}\n"
            f"  Total Cost: {metrics.get('total_cost', 0):.1f}\n"
            f"  Resilience Index: {metrics.get('avg_resilience', 0):.3f}\n\n"
        )

        prompt += (
            "TASK:\n"
            "Explain why resources were allocated this way at this time step. "
            "Reference specific zone names, severity values, and agent priorities. "
            "Mention any significant trade-offs."
        )

        return prompt

    @staticmethod
    def build_query_prompt(question: str, simulation_state: dict) -> str:
        """Build the User Query prompt (Section 20.3)."""
        # Compact state summary
        zones = simulation_state.get("final_zone_states", [])
        metrics = simulation_state.get("final_metrics", {})
        alloc_history = simulation_state.get("allocation_history", [])

        prompt = "SIMULATION DATA:\n"
        prompt += f"Scenario: {simulation_state.get('scenario', {}).get('name', 'Unknown')}\n"
        prompt += f"Steps completed: {simulation_state.get('total_steps_completed', 0)}\n\n"

        prompt += "CURRENT ZONE STATUS:\n"
        for z in zones:
            prompt += f"  {z['name']}: Severity={z['current_severity']}/10, Pop={z['population']}, "
            prompt += f"Resources Received={z['cumulative_resources_received']:.1f}, "
            prompt += f"Unmet Demand={z['unmet_demand']:.1f}\n"

        prompt += f"\nFINAL METRICS:\n"
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                prompt += f"  {k}: {v}\n"

        if alloc_history:
            prompt += f"\nRECENT ALLOCATIONS (last 3 steps):\n"
            for ah in alloc_history[-3:]:
                prompt += f"  Step {ah.get('step', '?')}: {ah.get('allocations', {})}\n"

        prompt += f"\nUSER QUESTION:\n{question}\n\nANSWER:"
        return prompt

    @staticmethod
    def build_insight_prompt(simulation_data: dict) -> str:
        """Build the Insight Report prompt (Section 20.4)."""
        metrics_history = simulation_data.get("metrics_history", [])
        alloc_history = simulation_data.get("allocation_history", [])
        final_zones = simulation_data.get("final_zone_states", [])
        scenario = simulation_data.get("scenario", {})

        prompt = "COMPLETE SIMULATION DATA:\n"
        prompt += f"Scenario: {scenario.get('name', 'Unknown')} ({scenario.get('type', '')})\n"
        prompt += f"Duration: {scenario.get('duration', 0)} steps\n"
        prompt += f"Total Resources: {scenario.get('total_resources', 0)}\n\n"

        prompt += "METRICS HISTORY:\n"
        for m in metrics_history:
            prompt += (f"  Step {m.get('step', '?')}: Coverage={m.get('response_coverage', 0):.3f}, "
                       f"Gini={m.get('gini_coefficient', 0):.3f}, "
                       f"Resilience={m.get('avg_resilience', 0):.3f}\n")

        prompt += "\nFINAL ZONE STATES:\n"
        for z in final_zones:
            prompt += (f"  {z['name']}: Severity={z['current_severity']:.1f}, "
                       f"Total Resources={z['cumulative_resources_received']:.1f}, "
                       f"Resilience={z['resilience_index']:.3f}\n")

        prompt += (
            "\nREPORT FORMAT:\n"
            "1. Executive Summary (2-3 sentences summarizing overall performance)\n"
            "2. Key Findings (3-5 bullet points with specific numbers)\n"
            "3. Critical Decision Points (identify 2-3 time steps where significant trade-offs occurred)\n"
            "4. Agent Analysis (which agents were most influential and when)\n"
            "5. Fairness Assessment (how equity evolved, referencing Gini values)\n\n"
            "Generate the report now:"
        )

        return prompt

    @staticmethod
    def build_scenario_prompt(scenario: dict) -> str:
        """Build the Scenario Narration prompt (Section 20.5)."""
        zones = scenario.get("zones", [])
        zone_names = [z["name"] for z in zones]
        severities = [z["severity"] for z in zones]
        populations = [z["population"] for z in zones]
        total_demand = sum(z.get("initial_demand", 0) for z in zones)

        prompt = (
            f"SCENARIO DATA:\n"
            f"Type: {scenario.get('type', 'Unknown')}\n"
            f"Zones: {len(zones)} ({', '.join(zone_names)})\n"
            f"Severity Range: {min(severities):.1f} to {max(severities):.1f}\n"
            f"Total Population at Risk: {sum(populations):,}\n"
            f"Available Resources: {scenario.get('total_resources', 0)} units\n"
            f"Estimated Total Demand: {total_demand} units\n"
            f"Key Challenge: {scenario.get('description', 'Multiple zones affected')}\n\n"
            f"Generate a brief scenario introduction:"
        )
        return prompt

    @staticmethod
    def get_system_prompt(prompt_type: str) -> str:
        """Get the appropriate system prompt by type."""
        prompts = {
            "explanation": PromptEngine.EXPLANATION_SYSTEM,
            "query": PromptEngine.QUERY_SYSTEM,
            "insight": PromptEngine.INSIGHT_SYSTEM,
            "scenario": PromptEngine.SCENARIO_SYSTEM
        }
        return prompts.get(prompt_type, PromptEngine.EXPLANATION_SYSTEM)

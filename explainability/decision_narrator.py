"""
Decision Narrator Module
Programmatic template-based explanation generation (fallback when LLM unavailable).
Per Section 26.2 Contingency Plan.
"""


class DecisionNarrator:
    """
    Generates natural-language explanations from structured data using templates.
    This is the fallback system when the LLM is unavailable.
    """

    @staticmethod
    def narrate_allocation(step_data: dict) -> str:
        """
        Generate a template-based explanation for a time step's allocation.

        Args:
            step_data: dict with zones, allocations, metrics, negotiation info
        """
        zones = step_data.get("zones", [])
        allocations = step_data.get("allocations", {})
        metrics = step_data.get("metrics", {})
        step = step_data.get("step", 0)
        phase = step_data.get("phase", "Unknown")
        dissent_scores = step_data.get("dissent_scores", {})

        if not allocations:
            return "No allocation data available for this time step."

        # Find highest and lowest allocation
        sorted_alloc = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
        total_alloc = sum(allocations.values())

        top_zone = sorted_alloc[0][0]
        top_amount = sorted_alloc[0][1]
        top_pct = round(top_amount / total_alloc * 100, 1) if total_alloc > 0 else 0

        # Find severity of top zone
        zone_map = {z["name"]: z for z in zones}
        top_severity = zone_map.get(top_zone, {}).get("current_severity", 0)
        top_population = zone_map.get(top_zone, {}).get("population", 0)

        # Gini
        gini = metrics.get("gini_coefficient", 0)
        if gini < 0.15:
            fairness_desc = "highly equitable"
        elif gini < 0.25:
            fairness_desc = "moderately fair"
        elif gini < 0.35:
            fairness_desc = "somewhat unequal"
        else:
            fairness_desc = "significantly unequal"

        # Highest dissent
        if dissent_scores:
            max_dissent_agent = max(dissent_scores, key=dissent_scores.get)
            max_dissent_val = dissent_scores[max_dissent_agent]
        else:
            max_dissent_agent = "None"
            max_dissent_val = 0

        # Build narrative
        narrative = (
            f"At time step {step} ({phase} phase), {top_zone} received the largest allocation "
            f"({top_amount:.1f} units, {top_pct}% of available) based on a severity of "
            f"{top_severity:.1f}/10 affecting {top_population:,} residents. "
            f"The overall Gini coefficient this step was {gini:.2f}, indicating {fairness_desc} distribution. "
        )

        if max_dissent_val > 0.1:
            narrative += (
                f"The {max_dissent_agent} Agent showed the highest dissent ({max_dissent_val:.2f}), "
                f"preferring a different allocation pattern."
            )

        return narrative

    @staticmethod
    def narrate_scenario(scenario: dict) -> str:
        """Generate a brief scenario introduction from scenario data."""
        zones = scenario.get("zones", [])
        zone_names = [z["name"] for z in zones]
        severities = [z["severity"] for z in zones]
        populations = [z["population"] for z in zones]

        total_pop = sum(populations)
        total_demand = sum(z.get("initial_demand", 0) for z in zones)
        total_resources = scenario.get("total_resources", 0)

        supply_ratio = round(total_resources / total_demand * 100, 0) if total_demand > 0 else 0

        narrative = (
            f"A {scenario['type'].lower()} disaster has affected the region, impacting "
            f"{len(zones)} zones: {', '.join(zone_names)}. "
            f"Severity ranges from {min(severities):.1f} to {max(severities):.1f} on a 10-point scale, "
            f"with {total_pop:,} people at risk across all zones. "
            f"Emergency responders have {total_resources} resource units available — "
            f"approximately {supply_ratio:.0f}% of total estimated demand."
        )
        return narrative

    @staticmethod
    def narrate_summary(simulation_data: dict) -> str:
        """Generate a post-simulation template summary."""
        metrics_history = simulation_data.get("metrics_history", [])
        final_zones = simulation_data.get("final_zone_states", [])
        scenario = simulation_data.get("scenario", {})

        if not metrics_history:
            return "No simulation data available for summary."

        total_steps = len(metrics_history)
        avg_coverage = sum(m.get("response_coverage", 0) for m in metrics_history) / total_steps
        avg_gini = sum(m.get("gini_coefficient", 0) for m in metrics_history) / total_steps
        final_severity = sum(z.get("current_severity", 0) for z in final_zones) / len(final_zones) if final_zones else 0
        avg_resilience = sum(z.get("resilience_index", 0) for z in final_zones) / len(final_zones) if final_zones else 0

        narrative = (
            f"Simulation Summary — {scenario.get('name', 'Scenario')}\n\n"
            f"Over {total_steps} time steps, the multi-agent system achieved:\n"
            f"• Average response coverage: {avg_coverage:.1%}\n"
            f"• Average Gini coefficient: {avg_gini:.3f}\n"
            f"• Final average severity: {final_severity:.2f}/10\n"
            f"• Final average resilience index: {avg_resilience:.3f}\n\n"
        )

        # Performance assessment
        if avg_coverage > 0.7:
            narrative += "Response coverage exceeded the target of 70%. "
        else:
            narrative += f"Response coverage ({avg_coverage:.1%}) fell short of the 70% target. "

        if avg_gini < 0.3:
            narrative += "Resource distribution maintained fairness within acceptable bounds."
        else:
            narrative += "Resource distribution showed some inequality across zones."

        return narrative

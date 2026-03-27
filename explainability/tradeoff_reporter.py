"""
Trade-off Reporter Module
Analyzes and reports trade-offs made during resource allocation decisions.
"""


class TradeoffReporter:
    """Analyzes trade-offs between competing criteria in allocation decisions."""

    @staticmethod
    def analyze_tradeoffs(allocation_result: dict, zones: list) -> dict:
        """
        Analyze trade-offs in the current allocation.

        Returns dict with identified trade-offs and their descriptions.
        """
        allocations = allocation_result.get("final_allocation", {})
        metrics = allocation_result.get("fairness_after", {})
        negotiation = allocation_result.get("negotiation_result", {})
        proposals = negotiation.get("proposals", {})

        tradeoffs = []
        zone_map = {z["name"]: z for z in zones}

        # Speed vs Fairness trade-off
        sorted_by_severity = sorted(zones, key=lambda z: z["current_severity"], reverse=True)
        sorted_by_alloc = sorted(allocations.items(), key=lambda x: x[1], reverse=True)

        if sorted_by_severity and sorted_by_alloc:
            top_severity_zone = sorted_by_severity[0]["name"]
            top_alloc_zone = sorted_by_alloc[0][0]

            if top_severity_zone == top_alloc_zone:
                tradeoffs.append({
                    "type": "Speed vs Fairness",
                    "description": f"Resources concentrated on {top_severity_zone} (highest severity) — "
                                   f"prioritizes speed over equitable distribution.",
                    "severity": "moderate"
                })

        # Cost vs Coverage
        for zone in zones:
            name = zone["name"]
            if zone["accessibility"] < 3 and allocations.get(name, 0) > 0:
                tradeoffs.append({
                    "type": "Cost vs Coverage",
                    "description": f"{name} has low accessibility ({zone['accessibility']:.1f}/10), "
                                   f"making resource delivery costly. Allocation maintained for coverage.",
                    "severity": "low"
                })

        # Agent disagreement analysis
        dissent = negotiation.get("dissent_scores", {})
        max_dissent_agent = max(dissent, key=dissent.get) if dissent else None
        if max_dissent_agent and dissent.get(max_dissent_agent, 0) > 0.2:
            tradeoffs.append({
                "type": "Inter-Agent Tension",
                "description": f"{max_dissent_agent} Agent showed significant dissent "
                               f"({dissent[max_dissent_agent]:.2f}), indicating unresolved tension.",
                "severity": "high"
            })

        return {
            "tradeoffs": tradeoffs,
            "count": len(tradeoffs),
            "summary": f"{len(tradeoffs)} trade-off(s) identified in this allocation step."
        }

    @staticmethod
    def compare_baselines(system_metrics: dict, baseline_metrics: dict) -> dict:
        """Compare system performance against baseline strategies."""
        comparisons = {}
        for metric_name in ["response_coverage", "gini_coefficient", "total_cost", "avg_resilience"]:
            sys_val = system_metrics.get(metric_name, 0)
            base_val = baseline_metrics.get(metric_name, 0)
            diff = sys_val - base_val

            if metric_name in ["gini_coefficient", "total_cost"]:
                # Lower is better
                better = diff < 0
            else:
                # Higher is better
                better = diff > 0

            comparisons[metric_name] = {
                "system": round(sys_val, 4),
                "baseline": round(base_val, 4),
                "difference": round(diff, 4),
                "system_better": better
            }

        return comparisons

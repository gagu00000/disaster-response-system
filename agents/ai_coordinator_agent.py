"""
AI Coordination Agent
Represents the intelligent system layer — computational agent for global optimization.
Primary Mandate: Optimize overall system performance. Honest broker in negotiations.
Per Section 3.1.4.
"""
from agents.base_agent import BaseAgent
from decision_engine.criteria_manager import CriteriaManager


class AICoordinatorAgent(BaseAgent):
    """
    AI Coordination Agent.
    Dynamic criteria weights based on disaster phase.
    Analyzes holistically, proposes balanced compromise solutions.
    Acts as mediator during negotiation.
    """

    def __init__(self):
        super().__init__("AI Coordinator")

    def _apply_behavioral_adjustments(self, proposal: dict, zones: list, total_resources: float) -> dict:
        """
        Balanced, data-driven allocation.
        No extreme concentration or spreading — aims for global optimality.
        Slight adjustments to prevent critical zones from being underserved.
        """
        zone_map = {z["name"]: z for z in zones}
        adjusted = proposal.copy()

        # Identify critically underserved zones
        for zone in zones:
            name = zone["name"]
            if name in adjusted:
                severity = zone["current_severity"]
                unmet = zone.get("unmet_demand", 0)

                # Boost if severity is very high and unmet demand exists
                if severity >= 7.0 and unmet > 10:
                    adjusted[name] = round(adjusted[name] * 1.15, 2)
                # Slight reduction for low-severity, well-served zones
                elif severity < 3.0 and unmet < 3:
                    adjusted[name] = round(adjusted[name] * 0.85, 2)

        # Renormalize to total resources
        total = sum(adjusted.values())
        if total > 0:
            scale = total_resources / total
            adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

        return adjusted

    def analyze_divergence(self, all_proposals: dict) -> dict:
        """
        Analyze agreement and disagreement across proposals (Round 2 of negotiation).
        Identifies zones where agents agree vs. contested zones.

        Args:
            all_proposals: dict mapping agent_type → {zone_name: amount}

        Returns:
            dict with agreed_zones, contested_zones, and analysis
        """
        if not all_proposals:
            return {"agreed_zones": [], "contested_zones": [], "analysis": {}}

        zone_names = set()
        for proposal in all_proposals.values():
            zone_names.update(proposal.keys())

        analysis = {}
        agreed_zones = []
        contested_zones = []

        for zone in zone_names:
            values = [p.get(zone, 0) for p in all_proposals.values()]
            mean_val = sum(values) / len(values) if values else 0
            max_val = max(values) if values else 0
            min_val = min(values) if values else 0

            # Coefficient of variation to detect disagreement
            if mean_val > 0:
                cv = (max_val - min_val) / mean_val
            else:
                cv = 0

            analysis[zone] = {
                "mean": round(mean_val, 2),
                "min": round(min_val, 2),
                "max": round(max_val, 2),
                "spread": round(max_val - min_val, 2),
                "cv": round(cv, 4),
                "contested": cv > 0.3  # Threshold for disagreement
            }

            if cv > 0.3:
                contested_zones.append(zone)
            else:
                agreed_zones.append(zone)

        return {
            "agreed_zones": agreed_zones,
            "contested_zones": contested_zones,
            "analysis": analysis
        }

    def compute_weighted_consensus(self, all_proposals: dict, zones: list) -> dict:
        """
        Compute weighted average of all agents' final positions (Round 4).
        Weights reflect domain authority per zone context.

        Args:
            all_proposals: dict mapping agent_type → {zone_name: amount}
            zones: list of zone state dicts

        Returns:
            Consensus allocation dict
        """
        zone_map = {z["name"]: z for z in zones}
        consensus = {}

        # Domain authority weights per context
        authority_weights = {
            "Emergency Response": 1.0,
            "Government Agency": 1.0,
            "NGO": 1.0,
            "AI Coordinator": 1.0
        }

        for zone in zone_map:
            severity = zone_map[zone]["current_severity"]
            vulnerability = zone_map[zone].get("vulnerability", 0.5)

            # Adjust authority weights based on zone context
            weights = authority_weights.copy()
            if severity >= 7:
                weights["Emergency Response"] = 1.5  # Emergency gets more say for critical zones
            if vulnerability >= 0.7:
                weights["NGO"] = 1.3  # NGO gets more say for vulnerable zones
            if severity < 4:
                weights["Government Agency"] = 1.3  # Government for low-severity planning

            total_weight = sum(weights.values())
            weighted_sum = 0
            for agent_type, proposal in all_proposals.items():
                agent_weight = weights.get(agent_type, 1.0) / total_weight
                weighted_sum += proposal.get(zone, 0) * agent_weight

            consensus[zone] = round(weighted_sum, 2)

        return consensus

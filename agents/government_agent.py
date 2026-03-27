"""
Government Agency Agent
Represents national disaster management, state/provincial offices, local government.
Primary Mandate: Policy compliance, budget management, balanced coverage.
Per Section 3.1.2.
"""
from agents.base_agent import BaseAgent


class GovernmentAgent(BaseAgent):
    """
    Government Agency Agent.
    Balances cost efficiency (0.35) with resilience (0.25).
    Conservative allocation spreading resources across more zones.
    Ensures no zone is visibly neglected (political accountability).
    """

    def __init__(self):
        super().__init__("Government Agency")

    def _apply_behavioral_adjustments(self, proposal: dict, zones: list, total_resources: float) -> dict:
        """
        Conservative allocation ensuring baseline coverage for every zone.
        Spreads resources more evenly, ensuring no zone gets zero.
        Caps maximum allocation to prevent over-concentration.
        """
        adjusted = proposal.copy()
        n_zones = len(zones)

        if n_zones == 0:
            return adjusted

        # Ensure minimum allocation (floor constraint) for every zone with severity > 0
        min_allocation = total_resources * 0.05  # At least 5% per zone
        max_allocation = total_resources * 0.35  # Cap at 35% per zone

        for zone in zones:
            name = zone["name"]
            if name in adjusted:
                if zone["current_severity"] > 0:
                    adjusted[name] = max(adjusted[name], min_allocation)
                adjusted[name] = min(adjusted[name], max_allocation)

        # Renormalize to total resources
        total = sum(adjusted.values())
        if total > 0:
            scale = total_resources / total
            adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

        return adjusted

"""
NGO Agent
Represents humanitarian organizations — Red Cross, Doctors Without Borders, UNICEF.
Primary Mandate: Equitable distribution. Advocate for vulnerable populations.
Per Section 3.1.3.
"""
from agents.base_agent import BaseAgent


class NGOAgent(BaseAgent):
    """
    NGO Agent.
    Strongly emphasizes fairness (0.45) and resilience (0.30).
    Equity-driven allocation ensuring no zone is disproportionately neglected.
    Considers vulnerability indices and population demographics.
    """

    def __init__(self):
        super().__init__("NGO")

    def _apply_behavioral_adjustments(self, proposal: dict, zones: list, total_resources: float) -> dict:
        """
        Equity-driven allocation adjusted by vulnerability.
        Boosts allocation to high-vulnerability, low-resource zones.
        Ensures proportional allocation relative to population and need.
        """
        zone_map = {z["name"]: z for z in zones}
        adjusted = proposal.copy()

        # Boost vulnerable and underserved zones
        for zone in zones:
            name = zone["name"]
            if name in adjusted:
                vulnerability = zone.get("vulnerability", 0.5)
                unmet = zone.get("unmet_demand", 0)
                cumulative = zone.get("cumulative_resources_received", 0)

                # Vulnerability boost: higher vulnerability → more resources
                vuln_factor = 1.0 + (vulnerability - 0.5) * 0.6

                # Underserved boost: if zone has received less than proportional share
                total_pop = sum(z["population"] for z in zones)
                pop_share = zone["population"] / total_pop if total_pop > 0 else 0
                fair_share = pop_share * total_resources

                if cumulative < fair_share * 0.5:
                    vuln_factor += 0.2  # Extra boost for underserved

                adjusted[name] = round(adjusted[name] * vuln_factor, 2)

        # Renormalize to total resources
        total = sum(adjusted.values())
        if total > 0:
            scale = total_resources / total
            adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

        return adjusted

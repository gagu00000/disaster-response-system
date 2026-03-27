"""
Emergency Response Agent
Represents first responders — fire departments, EMS, search and rescue, law enforcement.
Primary Mandate: Save lives. Minimize casualties. Reach critical zones fastest.
Per Section 3.1.1.
"""
from agents.base_agent import BaseAgent


class EmergencyAgent(BaseAgent):
    """
    Emergency Response Agent.
    Heavily prioritizes speed (0.50) and resilience (0.30).
    Aggressively allocates toward high-severity zones.
    Tolerates higher costs for faster response.
    """

    def __init__(self):
        super().__init__("Emergency Response")

    def _apply_behavioral_adjustments(self, proposal: dict, zones: list, total_resources: float) -> dict:
        """
        Aggressive allocation toward high-severity zones.
        Concentrates resources on the most critical areas, even at the
        expense of moderate-severity zones.
        """
        zone_map = {z["name"]: z for z in zones}
        adjusted = proposal.copy()

        # Identify highest severity zones
        severity_sorted = sorted(zones, key=lambda z: z["current_severity"], reverse=True)
        top_severe = [z["name"] for z in severity_sorted[:2]]  # Top 2 most severe

        # Boost allocation to highest severity zones
        boost_factor = 1.3
        reduce_factor = 0.7

        for zone_name in adjusted:
            if zone_name in top_severe:
                adjusted[zone_name] = round(adjusted[zone_name] * boost_factor, 2)
            else:
                adjusted[zone_name] = round(adjusted[zone_name] * reduce_factor, 2)

        # Renormalize to total resources
        total = sum(adjusted.values())
        if total > 0:
            scale = total_resources / total
            adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

        return adjusted

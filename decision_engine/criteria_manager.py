"""
Criteria Manager Module
Manages agent-specific criteria weight profiles and dynamic phase-based re-weighting.
Per Section 3.1 and Section 3.1.4 of the implementation plan.
"""


class CriteriaManager:
    """
    Manages criteria weight profiles for all agents and handles
    dynamic phase-based weight adaptation for the AI Coordinator.
    """

    # Agent criteria weight profiles (Section 3.1)
    AGENT_PROFILES = {
        "Emergency Response": {
            "speed": 0.50,
            "fairness": 0.10,
            "cost": 0.10,
            "resilience": 0.30
        },
        "Government Agency": {
            "speed": 0.20,
            "fairness": 0.20,
            "cost": 0.35,
            "resilience": 0.25
        },
        "NGO": {
            "speed": 0.15,
            "fairness": 0.45,
            "cost": 0.10,
            "resilience": 0.30
        },
        "AI Coordinator": {
            # Default (Phase 1) — will be overridden dynamically
            "speed": 0.45,
            "fairness": 0.20,
            "cost": 0.10,
            "resilience": 0.25
        }
    }

    # AI Coordinator dynamic phase weights (Section 3.1.4)
    AI_PHASE_WEIGHTS = {
        "Immediate Response": {"speed": 0.45, "fairness": 0.20, "cost": 0.10, "resilience": 0.25},
        "Stabilization": {"speed": 0.25, "fairness": 0.30, "cost": 0.20, "resilience": 0.25},
        "Recovery": {"speed": 0.10, "fairness": 0.25, "cost": 0.30, "resilience": 0.35}
    }

    @staticmethod
    def get_agent_weights(agent_type: str, phase: str = None) -> dict:
        """
        Get criteria weights for an agent.
        For AI Coordinator, dynamically adjusts based on disaster phase.

        Args:
            agent_type: one of 'Emergency Response', 'Government Agency', 'NGO', 'AI Coordinator'
            phase: current disaster phase name (required for AI Coordinator)

        Returns:
            dict with criteria weights
        """
        if agent_type == "AI Coordinator" and phase:
            return CriteriaManager.AI_PHASE_WEIGHTS.get(
                phase,
                CriteriaManager.AGENT_PROFILES["AI Coordinator"]
            ).copy()

        if agent_type in CriteriaManager.AGENT_PROFILES:
            return CriteriaManager.AGENT_PROFILES[agent_type].copy()

        # Fallback: equal weights
        return {"speed": 0.25, "fairness": 0.25, "cost": 0.25, "resilience": 0.25}

    @staticmethod
    def get_all_agent_types() -> list:
        """Return list of all agent type names."""
        return list(CriteriaManager.AGENT_PROFILES.keys())

    @staticmethod
    def validate_weights(weights: dict) -> bool:
        """Check that weights sum to approximately 1.0."""
        total = sum(weights.values())
        return abs(total - 1.0) < 0.01

    @staticmethod
    def normalize_weights(weights: dict) -> dict:
        """Normalize weights to sum to 1.0."""
        total = sum(weights.values())
        if total == 0:
            n = len(weights)
            return {k: 1.0 / n for k in weights}
        return {k: round(v / total, 4) for k, v in weights.items()}

    @staticmethod
    def get_weight_description(agent_type: str) -> str:
        """Return a human-readable description of the agent's weighting priorities."""
        descriptions = {
            "Emergency Response": "Heavily prioritizes response speed (50%) and resilience (30%), minimal focus on fairness and cost.",
            "Government Agency": "Balances cost efficiency (35%) with resilience (25%), moderate attention to speed and fairness.",
            "NGO": "Strongly emphasizes fairness (45%) and resilience (30%), accepts slower response and higher costs.",
            "AI Coordinator": "Dynamic weights adapting to disaster phase — speed-focused early, cost/resilience-focused later."
        }
        return descriptions.get(agent_type, "Balanced criteria weighting.")

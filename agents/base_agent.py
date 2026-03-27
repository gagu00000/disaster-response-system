"""
Base Agent Module
Abstract agent interface defining the common structure for all agent types.
Per Section 3.1 of the implementation plan.
"""
from abc import ABC, abstractmethod
from decision_engine.priority_aggregator import PriorityAggregator
from decision_engine.criteria_manager import CriteriaManager


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    Each agent independently evaluates zones and proposes resource allocations.
    """

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.priority_aggregator = PriorityAggregator()
        self.weights = CriteriaManager.get_agent_weights(agent_type)
        self.description = CriteriaManager.get_weight_description(agent_type)

        # State tracking
        self.current_priorities = None
        self.current_proposal = None
        self.evaluation_log = []

    def evaluate_zones(self, zones: list, phase: str = None) -> dict:
        """
        Independently evaluate all zones using the decision engine.
        Returns priority rankings from this agent's perspective.
        """
        # Update weights for phase (primarily for AI Coordinator)
        self.weights = CriteriaManager.get_agent_weights(self.agent_type, phase)

        # Compute priorities using AHP + Fuzzy Logic
        self.current_priorities = self.priority_aggregator.compute_agent_priorities(
            self.agent_type, zones, phase
        )

        # Log evaluation
        self.evaluation_log.append({
            "phase": phase,
            "weights": self.weights.copy(),
            "priorities": self.current_priorities
        })

        return self.current_priorities

    def propose_allocation(self, zones: list, total_resources: float, phase: str = None) -> dict:
        """
        Generate a resource allocation proposal based on this agent's priorities.

        Returns:
            dict mapping zone_name → proposed_resource_amount
        """
        if self.current_priorities is None:
            self.evaluate_zones(zones, phase)

        composite_scores = self.current_priorities["composite_scores"]
        total_score = sum(composite_scores.values())

        if total_score == 0:
            # Equal distribution fallback
            n = len(zones)
            per_zone = total_resources / n if n > 0 else 0
            proposal = {z["name"]: round(per_zone, 2) for z in zones}
        else:
            # Proportional to priority scores
            proposal = {}
            for zone_name, score in composite_scores.items():
                proportion = score / total_score
                proposal[zone_name] = round(proportion * total_resources, 2)

        # Apply agent-specific adjustments
        proposal = self._apply_behavioral_adjustments(proposal, zones, total_resources)

        self.current_proposal = proposal
        return proposal

    @abstractmethod
    def _apply_behavioral_adjustments(self, proposal: dict, zones: list, total_resources: float) -> dict:
        """
        Apply agent-specific behavioral adjustments to the base proposal.
        Each agent type implements its own behavioral characteristics.
        """
        pass

    def make_concession(self, own_proposal: dict, other_proposals: list,
                         contested_zones: list, concession_rate: float = 0.3) -> dict:
        """
        Adjust proposal for contested zones, moving toward compromise.

        Args:
            own_proposal: this agent's current proposal
            other_proposals: list of other agents' proposals
            contested_zones: zones where agents disagree
            concession_rate: how much to concede (0-1)

        Returns:
            Adjusted proposal
        """
        adjusted = own_proposal.copy()

        for zone in contested_zones:
            if zone in adjusted:
                # Average of other proposals for this zone
                others_avg = 0
                count = 0
                for op in other_proposals:
                    if zone in op:
                        others_avg += op[zone]
                        count += 1
                if count > 0:
                    others_avg /= count
                    # Move toward the average by concession_rate
                    adjusted[zone] = round(
                        adjusted[zone] * (1 - concession_rate) + others_avg * concession_rate, 2
                    )

        # Renormalize to total resources
        total = sum(adjusted.values())
        if total > 0:
            target_total = sum(own_proposal.values())
            scale = target_total / total
            adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

        return adjusted

    def compute_dissent(self, own_proposal: dict, consensus: dict) -> float:
        """
        Compute how far this agent's proposal is from the consensus.
        Higher dissent = more disagreement.
        """
        if not own_proposal or not consensus:
            return 0.0

        total_diff = 0
        total_value = 0
        for zone in own_proposal:
            if zone in consensus:
                total_diff += abs(own_proposal[zone] - consensus[zone])
                total_value += own_proposal[zone]

        if total_value == 0:
            return 0.0
        return round(total_diff / total_value, 4)

    def get_state(self) -> dict:
        """Return agent's current state for logging/display."""
        return {
            "agent_type": self.agent_type,
            "weights": self.weights,
            "description": self.description,
            "current_proposal": self.current_proposal,
            "priorities": {
                "ranking": self.current_priorities["ranking"] if self.current_priorities else [],
                "composite_scores": self.current_priorities["composite_scores"] if self.current_priorities else {}
            }
        }

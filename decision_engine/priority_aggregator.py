"""
Priority Aggregator Module
Combines fuzzy logic scores with AHP criteria weights to produce composite priority scores.
Implements Section 4.4: Integration of AHP and Fuzzy Logic.
"""
from decision_engine.ahp_module import AHPModule
from decision_engine.fuzzy_module import FuzzyModule
from decision_engine.criteria_manager import CriteriaManager


class PriorityAggregator:
    """
    Aggregates fuzzy criterion scores using AHP-derived weights
    to produce composite priority scores for each zone per agent.
    """

    def __init__(self):
        self.ahp = AHPModule()
        self.fuzzy = FuzzyModule()

    def compute_agent_priorities(self, agent_type: str, zones: list, phase: str = None) -> dict:
        """
        Compute composite priority scores for all zones from one agent's perspective.

        Process (Section 4.4):
        1. Fuzzy Logic computes a priority score per zone per criterion
        2. AHP provides the criteria weight vector for the agent
        3. Composite score = weighted sum of fuzzy criterion scores

        Args:
            agent_type: agent name
            zones: list of zone state dicts
            phase: current disaster phase

        Returns:
            dict with zone rankings, scores, and AHP details
        """
        # Step 1: Get agent's criteria weights
        raw_weights = CriteriaManager.get_agent_weights(agent_type, phase)

        # Step 2: Run AHP to validate/compute weights
        ahp_result = AHPModule.compute_weights(raw_weights)
        weights = ahp_result["weights"]

        # Step 3: Compute per-criterion fuzzy scores for each zone
        criterion_scores = self.fuzzy.compute_criterion_scores(zones)

        # Step 4: Compute composite scores using AHP weights
        composite_scores = AHPModule.score_alternatives(criterion_scores, weights)

        # Step 5: Rank zones by composite score (descending)
        ranked = sorted(composite_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "agent_type": agent_type,
            "weights": weights,
            "ahp_consistency_ratio": ahp_result["consistency_ratio"],
            "ahp_is_consistent": ahp_result["is_consistent"],
            "criterion_scores": criterion_scores,
            "composite_scores": composite_scores,
            "ranking": [{"zone": name, "score": score, "rank": i + 1} for i, (name, score) in enumerate(ranked)]
        }

    def compute_all_agent_priorities(self, zones: list, phase: str = None) -> dict:
        """
        Compute priorities for all four agents.

        Returns:
            dict mapping agent_type → priority results
        """
        results = {}
        for agent_type in CriteriaManager.get_all_agent_types():
            results[agent_type] = self.compute_agent_priorities(agent_type, zones, phase)
        return results

    @staticmethod
    def compute_consensus_scores(all_priorities: dict) -> dict:
        """
        Compute a simple average of all agents' composite scores as a starting point.

        Args:
            all_priorities: output of compute_all_agent_priorities

        Returns:
            dict mapping zone_name → average_score
        """
        zone_scores = {}
        agent_count = len(all_priorities)

        for agent_type, priority_data in all_priorities.items():
            for zone_name, score in priority_data["composite_scores"].items():
                if zone_name not in zone_scores:
                    zone_scores[zone_name] = 0.0
                zone_scores[zone_name] += score

        return {zone: round(total / agent_count, 4) for zone, total in zone_scores.items()}

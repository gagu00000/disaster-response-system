"""
Resource Allocator Module
Orchestrates the complete allocation pipeline: demand assessment, priority-weighted allocation,
constraint satisfaction, and fairness check/redistribution.
Per Section 5.1.
"""
from allocation.fairness_monitor import FairnessMonitor
from allocation.constraint_handler import ConstraintHandler
from agents.negotiation_engine import NegotiationEngine


class ResourceAllocator:
    """
    Orchestrates the full resource allocation pipeline for each time step:
    1. Demand Assessment
    2. Agent Negotiation → Consensus Allocation
    3. Constraint Satisfaction
    4. Fairness Check & Redistribution
    """

    def __init__(self):
        self.negotiation_engine = NegotiationEngine()
        self.fairness_monitor = FairnessMonitor()
        self.constraint_handler = ConstraintHandler()
        self.allocation_log = []

    def reset(self):
        """Reset for a new simulation."""
        self.negotiation_engine.reset_agents()
        self.allocation_log = []

    def allocate(self, zones: list, total_resources: float, phase: str = None) -> dict:
        """
        Execute the complete allocation pipeline for one time step.

        Args:
            zones: list of zone state dicts
            total_resources: available resources
            phase: current disaster phase

        Returns:
            dict with final allocations, negotiation results, fairness data, constraints
        """
        # Step 1: Run multi-agent negotiation
        negotiation_result = self.negotiation_engine.run_negotiation(zones, total_resources, phase)
        consensus = negotiation_result["consensus_allocation"]

        # Step 2: Apply constraints
        constrained = self.constraint_handler.apply_constraints(consensus, zones, total_resources)

        # Step 3: Fairness check
        fairness = self.fairness_monitor.check_fairness(constrained, zones)

        # Step 4: Redistribute if unfair
        if not fairness["is_fair"]:
            redistributed = self.fairness_monitor.redistribute(constrained, zones, total_resources)
            # Re-apply constraints after redistribution
            final_allocation = self.constraint_handler.apply_constraints(
                redistributed, zones, total_resources
            )
            fairness_after = self.fairness_monitor.check_fairness(final_allocation, zones)
        else:
            final_allocation = constrained
            fairness_after = fairness

        # Validate
        validation = self.constraint_handler.validate_allocation(final_allocation, zones, total_resources)

        # Build result
        result = {
            "final_allocation": final_allocation,
            "negotiation_result": negotiation_result,
            "pre_constraint_allocation": consensus,
            "post_constraint_allocation": constrained,
            "fairness_before": fairness,
            "fairness_after": fairness_after,
            "was_redistributed": not fairness["is_fair"],
            "validation": validation,
            "total_allocated": sum(final_allocation.values()),
            "total_available": total_resources
        }

        self.allocation_log.append(result)
        return result

    def get_allocation_log(self) -> list:
        """Return the complete allocation log."""
        return self.allocation_log

    def get_baseline_equal(self, zones: list, total_resources: float) -> dict:
        """Baseline 1: Equal allocation regardless of need."""
        n = len(zones)
        per_zone = total_resources / n if n > 0 else 0
        return {z["name"]: round(per_zone, 2) for z in zones}

    def get_baseline_severity(self, zones: list, total_resources: float) -> dict:
        """Baseline 2: Proportional to severity only."""
        total_severity = sum(z["current_severity"] for z in zones)
        if total_severity == 0:
            return self.get_baseline_equal(zones, total_resources)
        return {
            z["name"]: round((z["current_severity"] / total_severity) * total_resources, 2)
            for z in zones
        }

    def get_baseline_single_agent(self, zones: list, total_resources: float, phase: str = None) -> dict:
        """Baseline 3: AI Coordinator alone, no negotiation."""
        from agents.ai_coordinator_agent import AICoordinatorAgent
        ai = AICoordinatorAgent()
        ai.evaluate_zones(zones, phase)
        return ai.propose_allocation(zones, total_resources, phase)

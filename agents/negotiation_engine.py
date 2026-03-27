"""
Negotiation Engine Module
Implements the 5-round structured negotiation protocol per Section 3.3.
Round 0: Independent Evaluation
Round 1: Proposal Exchange
Round 2: Divergence Analysis
Round 3: Counter-Proposals
Round 4: Weighted Consensus
Round 5: Agreement & Execution
"""
from agents.emergency_agent import EmergencyAgent
from agents.government_agent import GovernmentAgent
from agents.ngo_agent import NGOAgent
from agents.ai_coordinator_agent import AICoordinatorAgent


class NegotiationEngine:
    """
    Implements the structured multi-agent negotiation protocol.
    Facilitates deliberation between all four agents to reach consensus allocation.
    """

    def __init__(self):
        self.agents = {
            "Emergency Response": EmergencyAgent(),
            "Government Agency": GovernmentAgent(),
            "NGO": NGOAgent(),
            "AI Coordinator": AICoordinatorAgent()
        }
        self.negotiation_log = []

    def reset_agents(self):
        """Reset all agents for a new simulation."""
        self.agents = {
            "Emergency Response": EmergencyAgent(),
            "Government Agency": GovernmentAgent(),
            "NGO": NGOAgent(),
            "AI Coordinator": AICoordinatorAgent()
        }
        self.negotiation_log = []

    def run_negotiation(self, zones: list, total_resources: float, phase: str = None) -> dict:
        """
        Execute the complete 5-round negotiation protocol.

        Args:
            zones: list of zone state dicts
            total_resources: available resources for this step
            phase: current disaster phase name

        Returns:
            dict with consensus allocation, negotiation log, agent states, dissent scores
        """
        negotiation_record = {
            "phase": phase,
            "total_resources": total_resources,
            "rounds": []
        }

        # --- ROUND 0: INDEPENDENT EVALUATION ---
        evaluations = {}
        for agent_type, agent in self.agents.items():
            evaluations[agent_type] = agent.evaluate_zones(zones, phase)

        negotiation_record["rounds"].append({
            "round": 0,
            "name": "Independent Evaluation",
            "description": "Each agent independently evaluates all zones using AHP + Fuzzy Logic",
            "evaluations": {
                at: {
                    "ranking": ev["ranking"],
                    "weights": ev["weights"]
                }
                for at, ev in evaluations.items()
            }
        })

        # --- ROUND 1: PROPOSAL EXCHANGE ---
        proposals = {}
        for agent_type, agent in self.agents.items():
            proposals[agent_type] = agent.propose_allocation(zones, total_resources, phase)

        negotiation_record["rounds"].append({
            "round": 1,
            "name": "Proposal Exchange",
            "description": "All agents simultaneously submit their allocation proposals",
            "proposals": {at: dict(p) for at, p in proposals.items()}
        })

        # --- ROUND 2: DIVERGENCE ANALYSIS ---
        ai_coordinator = self.agents["AI Coordinator"]
        divergence = ai_coordinator.analyze_divergence(proposals)

        negotiation_record["rounds"].append({
            "round": 2,
            "name": "Divergence Analysis",
            "description": "AI Coordinator analyzes agreement/disagreement. Agreed zones locked.",
            "agreed_zones": divergence["agreed_zones"],
            "contested_zones": divergence["contested_zones"],
            "analysis": divergence["analysis"]
        })

        # --- ROUND 3: COUNTER-PROPOSALS ---
        contested_zones = divergence["contested_zones"]
        counter_proposals = {}

        if contested_zones:
            for agent_type, agent in self.agents.items():
                other_proposals = [p for at, p in proposals.items() if at != agent_type]
                counter = agent.make_concession(
                    proposals[agent_type],
                    other_proposals,
                    contested_zones,
                    concession_rate=0.3
                )
                counter_proposals[agent_type] = counter
        else:
            counter_proposals = proposals

        negotiation_record["rounds"].append({
            "round": 3,
            "name": "Counter-Proposals",
            "description": "Agents submit adjusted positions for contested zones with concessions",
            "counter_proposals": {at: dict(p) for at, p in counter_proposals.items()}
        })

        # --- ROUND 4: WEIGHTED CONSENSUS ---
        final_proposals = counter_proposals if counter_proposals else proposals
        consensus = ai_coordinator.compute_weighted_consensus(final_proposals, zones)

        # Ensure total doesn't exceed available resources
        total_allocated = sum(consensus.values())
        if total_allocated > total_resources:
            scale = total_resources / total_allocated
            consensus = {k: round(v * scale, 2) for k, v in consensus.items()}

        negotiation_record["rounds"].append({
            "round": 4,
            "name": "Weighted Consensus",
            "description": "AI Coordinator computes weighted average of all agents' final positions",
            "consensus_allocation": dict(consensus)
        })

        # --- ROUND 5: AGREEMENT & EXECUTION ---
        dissent_scores = {}
        for agent_type, agent in self.agents.items():
            dissent_scores[agent_type] = agent.compute_dissent(
                proposals[agent_type], consensus
            )

        negotiation_record["rounds"].append({
            "round": 5,
            "name": "Agreement & Execution",
            "description": "Final allocation declared. Dissent scores recorded.",
            "final_allocation": dict(consensus),
            "dissent_scores": dissent_scores
        })

        # Store in log
        self.negotiation_log.append(negotiation_record)

        # Build result
        return {
            "consensus_allocation": consensus,
            "proposals": {at: dict(p) for at, p in proposals.items()},
            "counter_proposals": {at: dict(p) for at, p in counter_proposals.items()},
            "divergence": divergence,
            "dissent_scores": dissent_scores,
            "negotiation_record": negotiation_record,
            "agent_states": {at: agent.get_state() for at, agent in self.agents.items()}
        }

    def get_negotiation_log(self) -> list:
        """Return the complete negotiation log for all rounds."""
        return self.negotiation_log

    def get_agent_states(self) -> dict:
        """Return current states of all agents."""
        return {at: agent.get_state() for at, agent in self.agents.items()}

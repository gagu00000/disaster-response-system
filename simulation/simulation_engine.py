"""
Simulation Engine Module
Manages the main time-step simulation loop.
Orchestrates: Environment Update → Observation → Decision → Execution → Impact → Metrics → Reporting
"""
from simulation.disaster_environment import DisasterEnvironment
from simulation.event_system import EventSystem
from simulation.impact_calculator import ImpactCalculator


class SimulationEngine:
    """
    Core simulation engine that runs the time-step loop.
    Each time step executes:
      Environment Update → Observation → Decision → Execution → Impact → Metrics → Reporting
    """

    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.environment = DisasterEnvironment(scenario)
        self.event_system = EventSystem(scenario)
        self.impact_calculator = ImpactCalculator()

        self.current_step = 0
        self.is_running = False
        self.is_complete = False

        # Logs
        self.step_logs = []
        self.metrics_history = []
        self.allocation_history = []
        self.event_history = []

    def initialize(self):
        """Initialize/reset the simulation to its starting state."""
        self.environment = DisasterEnvironment(self.scenario)
        self.event_system = EventSystem(self.scenario)
        self.current_step = 0
        self.is_running = False
        self.is_complete = False
        self.step_logs = []
        self.metrics_history = []
        self.allocation_history = []
        self.event_history = []

    def get_current_state(self) -> dict:
        """Get the complete current state of the simulation."""
        return {
            "step": self.current_step,
            "total_steps": self.environment.duration,
            "phase": self.environment.get_current_phase(),
            "phase_info": self.environment.get_phase_info(),
            "is_running": self.is_running,
            "is_complete": self.is_complete,
            "environment": self.environment.get_environment_summary(),
            "zones": self.environment.get_all_zone_states(),
            "remaining_resources": self.environment.remaining_resources
        }

    def apply_dynamic_events(self) -> list:
        """Apply any dynamic events scheduled for the current time step."""
        applied = self.event_system.apply_events(self.current_step, self.environment)
        if applied:
            self.event_history.extend(applied)
        return applied

    def execute_allocation(self, allocations: dict) -> dict:
        """
        Execute a resource allocation plan.
        Returns the resulting metrics.
        """
        # Apply allocations to environment
        self.environment.apply_allocations(allocations)

        # Record allocation
        self.allocation_history.append({
            "step": self.current_step,
            "allocations": dict(allocations),
            "remaining_resources_after": round(self.environment.remaining_resources, 2)
        })

        # Compute metrics
        zones_state = self.environment.get_all_zone_states()
        metrics = self.impact_calculator.compute_all_metrics(
            zones_state, allocations, self.environment.total_resources
        )
        metrics["step"] = self.current_step
        metrics["phase"] = self.environment.get_current_phase()
        self.metrics_history.append(metrics)

        return metrics

    def advance_step(self):
        """Advance the simulation by one time step."""
        self.environment.advance_step()
        self.current_step = self.environment.current_step

        if self.current_step >= self.environment.duration:
            self.is_complete = True
            self.is_running = False

    def run_step(self, allocations: dict) -> dict:
        """
        Execute one complete simulation step:
        1. Apply dynamic events
        2. Execute allocations
        3. Compute metrics
        4. Advance time step
        Returns step result dictionary.
        """
        if self.is_complete:
            return {"error": "Simulation is complete", "step": self.current_step}

        self.is_running = True

        # Step 1: Apply dynamic events
        events = self.apply_dynamic_events()

        # Step 2: Get pre-allocation state (observation)
        pre_state = self.environment.get_all_zone_states()

        # Step 3: Execute allocation
        metrics = self.execute_allocation(allocations)

        # Step 4: Get post-allocation state
        post_state = self.environment.get_all_zone_states()

        # Build step log
        step_log = {
            "step": self.current_step,
            "phase": self.environment.get_current_phase(),
            "events_applied": events,
            "pre_allocation_zones": pre_state,
            "allocations": dict(allocations),
            "post_allocation_zones": post_state,
            "metrics": metrics,
            "remaining_resources": round(self.environment.remaining_resources, 2)
        }
        self.step_logs.append(step_log)

        # Step 5: Advance
        self.advance_step()

        return step_log

    def get_simulation_summary(self) -> dict:
        """Get complete simulation summary for post-simulation analysis."""
        return {
            "scenario": {
                "id": self.scenario["id"],
                "name": self.scenario["name"],
                "type": self.scenario["type"],
                "duration": self.scenario["duration"],
                "total_resources": self.scenario["total_resources"],
                "zone_count": len(self.scenario["zones"])
            },
            "total_steps_completed": self.current_step,
            "is_complete": self.is_complete,
            "final_zone_states": self.environment.get_all_zone_states(),
            "metrics_history": self.metrics_history,
            "allocation_history": self.allocation_history,
            "event_history": self.event_history,
            "step_logs": self.step_logs,
            "final_metrics": self.metrics_history[-1] if self.metrics_history else {}
        }

"""
Disaster Environment Module
Manages zone states, resource pools, and world state for the simulation.
"""
import copy


class Zone:
    """Represents a single disaster-affected zone with all state variables."""

    def __init__(self, zone_data: dict):
        self.name = zone_data["name"]
        self.initial_severity = zone_data["severity"]
        self.current_severity = zone_data["severity"]
        self.population = zone_data["population"]
        self.accessibility = zone_data["accessibility"]
        self.resource_availability = zone_data["resource_availability"]
        self.vulnerability = zone_data.get("vulnerability", 0.5)
        self.initial_demand = zone_data.get("initial_demand", 20)

        # Dynamic state variables (Section 6.3)
        self.unmet_demand = self.initial_demand
        self.cumulative_resources_received = 0
        self.resources_received_this_step = 0
        self.resilience_index = 0.5
        self.population_at_risk = int(self.population * (self.current_severity / 10.0))

    def update_population_at_risk(self):
        """Recalculate population at risk based on current severity."""
        self.population_at_risk = int(self.population * (self.current_severity / 10.0))

    def apply_resources(self, amount: float):
        """Apply resource allocation to this zone."""
        self.resources_received_this_step = amount
        self.cumulative_resources_received += amount
        # Reduce unmet demand
        self.unmet_demand = max(0, self.unmet_demand - amount)
        # Reduce severity based on resources (diminishing returns)
        severity_reduction = min(amount * 0.05, self.current_severity * 0.15)
        self.current_severity = max(0, self.current_severity - severity_reduction)
        # Improve resilience
        if self.initial_demand > 0:
            coverage_ratio = self.cumulative_resources_received / (self.initial_demand * 3)
            self.resilience_index = min(1.0, 0.3 + coverage_ratio * 0.7)
        self.update_population_at_risk()

    def apply_event(self, severity_change: float, accessibility_change: float):
        """Apply a dynamic event's effects to this zone."""
        self.current_severity = max(0, min(10, self.current_severity + severity_change))
        self.accessibility = max(0, min(10, self.accessibility + accessibility_change))
        # Increase unmet demand on severity increase
        if severity_change > 0:
            self.unmet_demand += severity_change * 3
        self.update_population_at_risk()

    def step_decay(self):
        """Natural per-step changes (slight severity decay, demand regeneration)."""
        # Small natural severity reduction each step
        self.current_severity = max(0, self.current_severity - 0.1)
        # Slight accessibility recovery
        self.accessibility = min(10, self.accessibility + 0.05)
        # Demand regenerates slightly
        self.unmet_demand = max(0, self.unmet_demand + 0.5)
        # Reset per-step tracking
        self.resources_received_this_step = 0
        self.update_population_at_risk()

    def get_state(self) -> dict:
        """Return a snapshot of the zone's current state."""
        return {
            "name": self.name,
            "current_severity": round(self.current_severity, 2),
            "population": self.population,
            "population_at_risk": self.population_at_risk,
            "accessibility": round(self.accessibility, 2),
            "resource_availability": round(self.resource_availability, 2),
            "vulnerability": self.vulnerability,
            "unmet_demand": round(self.unmet_demand, 2),
            "cumulative_resources_received": round(self.cumulative_resources_received, 2),
            "resources_received_this_step": round(self.resources_received_this_step, 2),
            "resilience_index": round(self.resilience_index, 4),
            "initial_demand": self.initial_demand
        }


class DisasterEnvironment:
    """
    Manages the complete disaster world state including all zones,
    the resource pool, and the current simulation phase.
    """

    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.scenario_id = scenario["id"]
        self.scenario_name = scenario["name"]
        self.scenario_type = scenario["type"]
        self.total_resources = scenario["total_resources"]
        self.remaining_resources = scenario["total_resources"]
        self.duration = scenario["duration"]
        self.current_step = 0
        self.current_phase = scenario["phases"][0]["name"] if scenario.get("phases") else "Unknown"
        self.phases = scenario.get("phases", [])

        # Initialize zones
        self.zones = [Zone(z) for z in scenario["zones"]]
        self.zone_names = [z.name for z in self.zones]

        # History tracking
        self.state_history = []

    def get_current_phase(self) -> str:
        """Determine the current disaster phase based on time step."""
        for phase in self.phases:
            if phase["start"] <= self.current_step <= phase["end"]:
                self.current_phase = phase["name"]
                return phase["name"]
        return self.current_phase

    def get_phase_info(self) -> dict:
        """Get full info about the current phase."""
        for phase in self.phases:
            if phase["start"] <= self.current_step <= phase["end"]:
                return phase
        return self.phases[-1] if self.phases else {"name": "Unknown", "description": ""}

    def get_all_zone_states(self) -> list:
        """Return state snapshots for all zones."""
        return [z.get_state() for z in self.zones]

    def get_zone_by_name(self, name: str) -> Zone:
        """Retrieve a zone object by name."""
        for z in self.zones:
            if z.name == name:
                return z
        raise ValueError(f"Zone '{name}' not found")

    def apply_allocations(self, allocations: dict):
        """
        Apply resource allocations to zones.
        allocations: dict mapping zone_name -> resource_amount
        """
        total_allocated = sum(allocations.values())
        if total_allocated > self.remaining_resources:
            # Scale down proportionally
            scale = self.remaining_resources / total_allocated if total_allocated > 0 else 0
            allocations = {k: v * scale for k, v in allocations.items()}
            total_allocated = self.remaining_resources

        for zone_name, amount in allocations.items():
            zone = self.get_zone_by_name(zone_name)
            zone.apply_resources(amount)

        self.remaining_resources -= total_allocated
        # Replenish some resources each step (supply chain)
        self.remaining_resources += self.total_resources * 0.08

    def advance_step(self):
        """Advance the simulation by one time step."""
        # Save current state to history
        self.state_history.append({
            "step": self.current_step,
            "phase": self.get_current_phase(),
            "zones": self.get_all_zone_states(),
            "remaining_resources": round(self.remaining_resources, 2)
        })
        # Apply natural decay to all zones
        for zone in self.zones:
            zone.step_decay()
        self.current_step += 1

    def get_total_demand(self) -> float:
        """Total unmet demand across all zones."""
        return sum(z.unmet_demand for z in self.zones)

    def get_environment_summary(self) -> dict:
        """Full summary of the environment state."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "scenario_type": self.scenario_type,
            "current_step": self.current_step,
            "total_steps": self.duration,
            "current_phase": self.get_current_phase(),
            "phase_info": self.get_phase_info(),
            "remaining_resources": round(self.remaining_resources, 2),
            "total_resources": self.total_resources,
            "total_demand": round(self.get_total_demand(), 2),
            "zones": self.get_all_zone_states(),
            "zone_names": self.zone_names
        }

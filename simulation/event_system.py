"""
Event System Module
Manages dynamic event scheduling and application during simulation.
Events include aftershocks, road closures, water level rises, plume shifts, etc.
"""


class DynamicEvent:
    """Represents a single dynamic event that occurs at a specific time step."""

    def __init__(self, event_data: dict):
        self.time_step = event_data["time_step"]
        self.event_type = event_data["type"]
        self.zone_name = event_data["zone"]
        self.description = event_data["description"]
        self.severity_change = event_data.get("severity_change", 0.0)
        self.accessibility_change = event_data.get("accessibility_change", 0.0)
        self.applied = False

    def to_dict(self) -> dict:
        return {
            "time_step": self.time_step,
            "type": self.event_type,
            "zone": self.zone_name,
            "description": self.description,
            "severity_change": self.severity_change,
            "accessibility_change": self.accessibility_change,
            "applied": self.applied
        }


class EventSystem:
    """
    Manages the schedule of dynamic events for a scenario.
    Applies events to the disaster environment at the correct time steps.
    """

    def __init__(self, scenario: dict):
        self.events = [DynamicEvent(e) for e in scenario.get("dynamic_events", [])]
        self.event_log = []

    def get_events_for_step(self, time_step: int) -> list:
        """Return all events scheduled for the given time step."""
        return [e for e in self.events if e.time_step == time_step and not e.applied]

    def apply_events(self, time_step: int, environment) -> list:
        """
        Apply all events for the given time step to the environment.
        Returns list of applied event descriptions.
        """
        applied_events = []
        step_events = self.get_events_for_step(time_step)

        for event in step_events:
            try:
                zone = environment.get_zone_by_name(event.zone_name)
                zone.apply_event(event.severity_change, event.accessibility_change)
                event.applied = True
                event_record = {
                    "time_step": time_step,
                    "type": event.event_type,
                    "zone": event.zone_name,
                    "description": event.description,
                    "severity_change": event.severity_change,
                    "accessibility_change": event.accessibility_change
                }
                applied_events.append(event_record)
                self.event_log.append(event_record)
            except ValueError:
                # Zone not found — skip event
                pass

        return applied_events

    def get_event_log(self) -> list:
        """Return the complete log of applied events."""
        return self.event_log

    def get_upcoming_events(self, current_step: int) -> list:
        """Return events scheduled for future steps."""
        return [e.to_dict() for e in self.events if e.time_step > current_step and not e.applied]

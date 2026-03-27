"""
Audit Trail Module
Manages complete decision logging for transparency and post-hoc analysis.
"""
import json
import os
from datetime import datetime


class AuditTrail:
    """
    Records and manages the complete audit trail of all decisions,
    allocations, and system events for transparency.
    """

    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
        self.entries = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log_entry(self, entry_type: str, data: dict):
        """Add an entry to the audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": entry_type,
            "data": data
        }
        self.entries.append(entry)

    def log_allocation(self, step: int, allocation: dict, metrics: dict, negotiation_summary: dict):
        """Log a resource allocation decision."""
        self.log_entry("allocation", {
            "step": step,
            "allocation": allocation,
            "metrics": metrics,
            "negotiation_summary": negotiation_summary
        })

    def log_event(self, step: int, event: dict):
        """Log a dynamic event."""
        self.log_entry("event", {"step": step, "event": event})

    def log_llm_interaction(self, prompt_type: str, prompt: str, response: str,
                             validation_result: dict, latency: float):
        """Log an LLM interaction."""
        self.log_entry("llm_interaction", {
            "prompt_type": prompt_type,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "validation": validation_result,
            "latency_seconds": latency
        })

    def get_entries(self, entry_type: str = None) -> list:
        """Get audit trail entries, optionally filtered by type."""
        if entry_type:
            return [e for e in self.entries if e["type"] == entry_type]
        return self.entries

    def get_summary(self) -> dict:
        """Get a summary of the audit trail."""
        return {
            "session_id": self.session_id,
            "total_entries": len(self.entries),
            "entry_types": {t: len([e for e in self.entries if e["type"] == t])
                           for t in set(e["type"] for e in self.entries)} if self.entries else {},
        }

    def save_to_file(self):
        """Save the audit trail to a JSON file."""
        os.makedirs(self.log_dir, exist_ok=True)
        filepath = os.path.join(self.log_dir, f"audit_{self.session_id}.json")
        with open(filepath, "w") as f:
            json.dump(self.entries, f, indent=2, default=str)
        return filepath

"""
Simulation Viewer Module
Provides time-step visualization and replay functionality.
Per Section 7.2 — visualization/simulation_viewer.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SimulationViewer:
    """
    Time-step visualization: zone state snapshots, event timeline,
    and allocation replay.
    """

    @staticmethod
    def create_step_snapshot(zones: list, allocations: dict, step: int, phase: str) -> go.Figure:
        """Create a snapshot visualization for a single simulation step."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Zone Severity & Resources", "Allocation This Step"],
            specs=[[{"type": "bar"}, {"type": "pie"}]]
        )

        zone_names = [z["name"] for z in zones]
        severities = [z["current_severity"] for z in zones]
        alloc_values = [allocations.get(z["name"], 0) for z in zones]

        # Severity bars
        fig.add_trace(go.Bar(
            x=zone_names, y=severities,
            name="Severity",
            marker_color=["#FF6B6B" if s >= 7 else "#FFEAA7" if s >= 4 else "#4ECDC4" for s in severities]
        ), row=1, col=1)

        # Allocation pie
        fig.add_trace(go.Pie(
            labels=zone_names, values=alloc_values,
            name="Allocation",
            marker=dict(colors=["#FF6B6B", "#FFEAA7", "#4ECDC4", "#45B7D1", "#96CEB4"])
        ), row=1, col=2)

        fig.update_layout(
            title=f"Step {step} — Phase: {phase}",
            template="plotly_dark",
            paper_bgcolor="#0a0a1a",
            plot_bgcolor="#0a0a1a",
            font=dict(color="#ccc"),
            height=400,
            showlegend=False
        )
        return fig

    @staticmethod
    def create_event_timeline(step_results: list) -> go.Figure:
        """Create a timeline of dynamic events across simulation steps."""
        steps = []
        event_labels = []
        event_colors = []

        for result in step_results:
            for event in result.get("events", []):
                steps.append(result["step"])
                event_labels.append(f"{event['type'].replace('_', ' ').title()}: {event['zone']}")
                color_map = {
                    "aftershock": "#FF6B6B",
                    "road_closure": "#FFEAA7",
                    "hospital_damage": "#FF9F43",
                    "water_level_rise": "#45B7D1",
                    "dam_breach_warning": "#FF6B6B",
                    "route_flooding": "#FFEAA7",
                    "chemical_plume_shift": "#A55EEA",
                    "secondary_explosion": "#FF6B6B",
                    "evacuation_order": "#FF9F43"
                }
                event_colors.append(color_map.get(event.get("type", ""), "#4ECDC4"))

        fig = go.Figure()
        if steps:
            fig.add_trace(go.Scatter(
                x=steps, y=event_labels,
                mode="markers+text",
                marker=dict(size=14, color=event_colors, symbol="diamond"),
                text=[f"Step {s}" for s in steps],
                textposition="top center",
                textfont=dict(size=9, color="#ccc")
            ))

        fig.update_layout(
            title="Dynamic Event Timeline",
            xaxis_title="Time Step",
            yaxis_title="Event",
            template="plotly_dark",
            paper_bgcolor="#0a0a1a",
            plot_bgcolor="#0a0a1a",
            font=dict(color="#ccc"),
            height=max(300, len(set(event_labels)) * 40 + 100)
        )
        return fig

    @staticmethod
    def create_severity_animation_frames(step_results: list) -> list:
        """Create data frames for animated severity progression."""
        frames = []
        for result in step_results:
            zones = result.get("post_state", [])
            frame = {
                "step": result["step"],
                "phase": result["phase"],
                "zone_names": [z["name"] for z in zones],
                "severities": [z["current_severity"] for z in zones],
                "resilience": [z["resilience_index"] for z in zones],
                "unmet_demand": [z["unmet_demand"] for z in zones]
            }
            frames.append(frame)
        return frames

    @staticmethod
    def create_allocation_replay(step_results: list) -> go.Figure:
        """Create a stacked bar chart showing allocation over all steps."""
        if not step_results:
            fig = go.Figure()
            fig.update_layout(title="No data", template="plotly_dark")
            return fig

        # Get all zone names from first step
        zones = step_results[0].get("post_state", [])
        zone_names = [z["name"] for z in zones]
        steps = [r["step"] for r in step_results]

        fig = go.Figure()
        colors = ["#FF6B6B", "#FFEAA7", "#4ECDC4", "#45B7D1", "#96CEB4", "#A55EEA"]

        for i, zname in enumerate(zone_names):
            values = [r.get("final_allocation", {}).get(zname, 0) for r in step_results]
            fig.add_trace(go.Bar(
                x=steps, y=values,
                name=zname,
                marker_color=colors[i % len(colors)]
            ))

        fig.update_layout(
            barmode="stack",
            title="Resource Allocation Replay (All Steps)",
            xaxis_title="Time Step",
            yaxis_title="Resources Allocated",
            template="plotly_dark",
            paper_bgcolor="#0a0a1a",
            plot_bgcolor="#0a0a1a",
            font=dict(color="#ccc"),
            height=450
        )
        return fig

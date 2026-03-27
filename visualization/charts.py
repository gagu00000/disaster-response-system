"""
Charts Module
Generates all visualizations for the dashboard using Plotly.
Covers all chart types from Section 9.1.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np


class Charts:
    """Generates all dashboard visualizations."""

    @staticmethod
    def resource_allocation_bar(allocations: dict, title: str = "Resource Allocation by Zone") -> go.Figure:
        """Grouped horizontal bar chart showing resource distribution per zone."""
        zones = list(allocations.keys())
        amounts = list(allocations.values())

        fig = go.Figure(go.Bar(
            x=amounts, y=zones, orientation='h',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'][:len(zones)],
            text=[f"{a:.1f}" for a in amounts],
            textposition='auto'
        ))
        fig.update_layout(
            title=title, xaxis_title="Resources Allocated",
            yaxis_title="Zone", height=400,
            template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    @staticmethod
    def agent_priority_radar(agent_weights: dict, title: str = "Agent Criteria Weights") -> go.Figure:
        """Radar/spider chart comparing how agents weight criteria differently."""
        categories = ['Speed', 'Fairness', 'Cost', 'Resilience']

        fig = go.Figure()
        colors = {'Emergency Response': '#FF6B6B', 'Government Agency': '#4ECDC4',
                  'NGO': '#45B7D1', 'AI Coordinator': '#96CEB4'}

        for agent_type, weights in agent_weights.items():
            values = [weights.get('speed', 0), weights.get('fairness', 0),
                      weights.get('cost', 0), weights.get('resilience', 0)]
            values.append(values[0])  # Close the loop

            fig.add_trace(go.Scatterpolar(
                r=values, theta=categories + [categories[0]],
                fill='toself', name=agent_type,
                line_color=colors.get(agent_type, '#888'),
                opacity=0.6
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 0.6])),
            title=title, showlegend=True, height=450,
            template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    @staticmethod
    def time_series_metrics(metrics_history: list) -> go.Figure:
        """Multi-line chart showing how metrics evolve over time."""
        if not metrics_history:
            return go.Figure()

        steps = [m.get("step", i) for i, m in enumerate(metrics_history)]
        coverage = [m.get("response_coverage", 0) for m in metrics_history]
        gini = [m.get("gini_coefficient", 0) for m in metrics_history]
        resilience = [m.get("avg_resilience", 0) for m in metrics_history]
        utilization = [m.get("resource_utilization", 0) for m in metrics_history]

        fig = make_subplots(rows=2, cols=2, subplot_titles=(
            "Response Coverage", "Gini Coefficient", "Avg Resilience", "Resource Utilization"
        ))

        fig.add_trace(go.Scatter(x=steps, y=coverage, name="Coverage", line=dict(color="#4ECDC4")), row=1, col=1)
        fig.add_trace(go.Scatter(x=steps, y=gini, name="Gini", line=dict(color="#FF6B6B")), row=1, col=2)
        fig.add_trace(go.Scatter(x=steps, y=resilience, name="Resilience", line=dict(color="#45B7D1")), row=2, col=1)
        fig.add_trace(go.Scatter(x=steps, y=utilization, name="Utilization", line=dict(color="#96CEB4")), row=2, col=2)

        # Add target lines
        fig.add_hline(y=0.70, line_dash="dash", line_color="green", opacity=0.5, row=1, col=1)
        fig.add_hline(y=0.30, line_dash="dash", line_color="red", opacity=0.5, row=1, col=2)
        fig.add_hline(y=0.60, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

        fig.update_layout(height=500, template="plotly_dark", showlegend=False,
                          margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @staticmethod
    def fairness_distribution(zones: list, allocations: dict) -> go.Figure:
        """Box/violin plot showing distributional equity."""
        zone_names = [z["name"] for z in zones]
        alloc_values = [allocations.get(z["name"], 0) for z in zones]
        populations = [z["population"] for z in zones]

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Allocation Distribution", "Per-Capita Allocation"))

        fig.add_trace(go.Bar(
            x=zone_names, y=alloc_values, name="Allocation",
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'][:len(zone_names)]
        ), row=1, col=1)

        per_capita = [a / p * 1000 if p > 0 else 0 for a, p in zip(alloc_values, populations)]
        fig.add_trace(go.Bar(
            x=zone_names, y=per_capita, name="Per Capita (×1000)",
            marker_color=['#FF9FF3', '#54A0FF', '#5F27CD', '#01A3A4', '#F368E0', '#EE5A24'][:len(zone_names)]
        ), row=1, col=2)

        fig.update_layout(height=400, template="plotly_dark", showlegend=False,
                          margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @staticmethod
    def negotiation_divergence(proposals: dict, consensus: dict) -> go.Figure:
        """Divergence bars showing agent proposals vs final consensus."""
        if not proposals or not consensus:
            return go.Figure()

        zones = list(consensus.keys())
        fig = go.Figure()

        colors = {'Emergency Response': '#FF6B6B', 'Government Agency': '#4ECDC4',
                  'NGO': '#45B7D1', 'AI Coordinator': '#96CEB4'}

        for agent_type, proposal in proposals.items():
            values = [proposal.get(z, 0) for z in zones]
            fig.add_trace(go.Bar(name=agent_type, x=zones, y=values,
                                 marker_color=colors.get(agent_type, '#888')))

        consensus_values = [consensus.get(z, 0) for z in zones]
        fig.add_trace(go.Scatter(
            x=zones, y=consensus_values, mode='markers+lines',
            name='Consensus', marker=dict(size=12, color='white', symbol='diamond'),
            line=dict(color='white', dash='dash', width=2)
        ))

        fig.update_layout(
            barmode='group', title="Agent Proposals vs Consensus",
            xaxis_title="Zone", yaxis_title="Proposed Resources",
            height=400, template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    @staticmethod
    def decision_heatmap(allocation_history: list, zone_names: list) -> go.Figure:
        """Heatmap showing complete spatial-temporal allocation pattern."""
        if not allocation_history:
            return go.Figure()

        steps = [h.get("step", i) for i, h in enumerate(allocation_history)]
        matrix = []
        for name in zone_names:
            row = [h.get("allocations", {}).get(name, 0) for h in allocation_history]
            matrix.append(row)

        fig = go.Figure(go.Heatmap(
            z=matrix, x=[f"Step {s}" for s in steps], y=zone_names,
            colorscale='YlOrRd', text=[[f"{v:.1f}" for v in row] for row in matrix],
            texttemplate="%{text}", hovertemplate="Zone: %{y}<br>Step: %{x}<br>Allocation: %{z:.1f}<extra></extra>"
        ))
        fig.update_layout(
            title="Resource Allocation Heatmap (Zone × Time Step)",
            height=350, template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    @staticmethod
    def criteria_weight_evolution(weight_history: list) -> go.Figure:
        """Stacked area chart showing AI Agent weight shifts over phases."""
        if not weight_history:
            return go.Figure()

        steps = list(range(len(weight_history)))
        speed = [w.get("speed", 0) for w in weight_history]
        fairness = [w.get("fairness", 0) for w in weight_history]
        cost = [w.get("cost", 0) for w in weight_history]
        resilience = [w.get("resilience", 0) for w in weight_history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=steps, y=speed, name='Speed', stackgroup='one',
                                  line=dict(color='#FF6B6B')))
        fig.add_trace(go.Scatter(x=steps, y=fairness, name='Fairness', stackgroup='one',
                                  line=dict(color='#4ECDC4')))
        fig.add_trace(go.Scatter(x=steps, y=cost, name='Cost', stackgroup='one',
                                  line=dict(color='#FFEAA7')))
        fig.add_trace(go.Scatter(x=steps, y=resilience, name='Resilience', stackgroup='one',
                                  line=dict(color='#45B7D1')))

        fig.update_layout(
            title="AI Coordinator Criteria Weight Evolution",
            xaxis_title="Time Step", yaxis_title="Weight",
            height=350, template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

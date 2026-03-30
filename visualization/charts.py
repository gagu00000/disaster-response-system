"""
Charts Module — Ultra-Dark Theme
Plotly visualizations with consistent #060610 backgrounds and neon accents.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── THEME ───
_BG = "#060610"
_PANEL = "#111119"
_GRID = "#1a1a2e"
_TEXT = "#e0e0e0"
_DIM = "#555"
_ACCENT = "#00d4aa"
_DANGER = "#ff3b30"
_WARN = "#ff6b35"
_BLUE = "#007aff"
_PURPLE = "#a855f7"
_COLORS = ["#ff3b30", "#00d4aa", "#007aff", "#a855f7", "#ff6b35", "#34c759"]

_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=_BG, plot_bgcolor=_BG,
    font=dict(family="Inter, sans-serif", color=_TEXT, size=12),
    margin=dict(l=16, r=16, t=44, b=16),
)

def _style_axes(fig):
    fig.update_xaxes(gridcolor=_GRID, zerolinecolor=_GRID)
    fig.update_yaxes(gridcolor=_GRID, zerolinecolor=_GRID)
    return fig


class Charts:

    @staticmethod
    def resource_allocation_bar(allocations: dict, title: str = "Resource Allocation") -> go.Figure:
        zones = list(allocations.keys())
        amounts = list(allocations.values())
        fig = go.Figure(go.Bar(
            x=amounts, y=zones, orientation='h',
            marker_color=_COLORS[:len(zones)],
            text=[f"{a:.1f}" for a in amounts], textposition='auto',
            textfont=dict(size=11, color=_TEXT)
        ))
        fig.update_layout(**_LAYOUT, title=title, height=350, showlegend=False, xaxis_title="Resources")
        return _style_axes(fig)

    @staticmethod
    def agent_priority_radar(agent_weights: dict, title: str = "Agent Criteria Weights") -> go.Figure:
        cats = ['Speed', 'Fairness', 'Cost', 'Resilience']
        fig = go.Figure()
        colors = {'Emergency Response': _DANGER, 'Government Agency': _BLUE,
                  'NGO': _ACCENT, 'AI Coordinator': _PURPLE}
        for agent, w in agent_weights.items():
            vals = [w.get('speed', 0), w.get('fairness', 0), w.get('cost', 0), w.get('resilience', 0)]
            vals.append(vals[0])
            fig.add_trace(go.Scatterpolar(
                r=vals, theta=cats + [cats[0]], fill='toself', name=agent,
                line=dict(color=colors.get(agent, '#888'), width=2), opacity=0.7
            ))
        fig.update_layout(
            **_LAYOUT,
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 0.6], gridcolor=_GRID, color=_DIM),
                angularaxis=dict(gridcolor=_GRID, color=_TEXT),
                bgcolor=_BG
            ),
            title=title, height=420, showlegend=True,
            legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)")
        )
        return fig

    @staticmethod
    def time_series_metrics(metrics_history: list) -> go.Figure:
        if not metrics_history:
            return go.Figure()
        steps = [m.get("step", i) for i, m in enumerate(metrics_history)]
        data = {
            "Response Coverage": ([m.get("response_coverage", 0) for m in metrics_history], _ACCENT),
            "Gini Coefficient": ([m.get("gini_coefficient", 0) for m in metrics_history], _DANGER),
            "Avg Resilience": ([m.get("avg_resilience", 0) for m in metrics_history], _BLUE),
            "Resource Utilization": ([m.get("resource_utilization", 0) for m in metrics_history], _PURPLE),
        }
        fig = make_subplots(rows=2, cols=2, subplot_titles=list(data.keys()),
                            horizontal_spacing=0.08, vertical_spacing=0.12)
        for idx, (name, (vals, color)) in enumerate(data.items()):
            r, c = (idx // 2) + 1, (idx % 2) + 1
            fig.add_trace(go.Scatter(
                x=steps, y=vals, name=name, line=dict(color=color, width=2),
                mode='lines+markers', marker=dict(size=5)
            ), row=r, col=c)
        # Target lines
        fig.add_hline(y=0.70, line_dash="dash", line_color=_ACCENT, opacity=0.3, row=1, col=1)
        fig.add_hline(y=0.30, line_dash="dash", line_color=_DANGER, opacity=0.3, row=1, col=2)
        fig.add_hline(y=0.60, line_dash="dash", line_color=_BLUE, opacity=0.3, row=2, col=1)
        fig.update_layout(**_LAYOUT, height=480, showlegend=False)
        return _style_axes(fig)

    @staticmethod
    def fairness_distribution(zones: list, allocations: dict) -> go.Figure:
        names = [z["name"] for z in zones]
        allocs = [allocations.get(z["name"], 0) for z in zones]
        pops = [z["population"] for z in zones]
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Allocation", "Per-Capita (×1000)"),
                            horizontal_spacing=0.1)
        fig.add_trace(go.Bar(x=names, y=allocs, marker_color=_COLORS[:len(names)],
                             text=[f"{a:.1f}" for a in allocs], textposition='auto'), row=1, col=1)
        pc = [a / p * 1000 if p > 0 else 0 for a, p in zip(allocs, pops)]
        fig.add_trace(go.Bar(x=names, y=pc, marker_color=[_PURPLE, _BLUE, _ACCENT, _WARN, _DANGER, "#34c759"][:len(names)],
                             text=[f"{v:.2f}" for v in pc], textposition='auto'), row=1, col=2)
        fig.update_layout(**_LAYOUT, height=360, showlegend=False)
        return _style_axes(fig)

    @staticmethod
    def negotiation_divergence(proposals: dict, consensus: dict) -> go.Figure:
        if not proposals or not consensus:
            return go.Figure()
        zones = list(consensus.keys())
        colors = {'Emergency Response': _DANGER, 'Government Agency': _BLUE,
                  'NGO': _ACCENT, 'AI Coordinator': _PURPLE}
        fig = go.Figure()
        for agent, prop in proposals.items():
            fig.add_trace(go.Bar(name=agent, x=zones, y=[prop.get(z, 0) for z in zones],
                                 marker_color=colors.get(agent, '#888'), opacity=0.8))
        fig.add_trace(go.Scatter(
            x=zones, y=[consensus.get(z, 0) for z in zones], mode='markers+lines',
            name='Consensus', marker=dict(size=10, color='white', symbol='diamond'),
            line=dict(color='white', dash='dash', width=2)
        ))
        fig.update_layout(**_LAYOUT, barmode='group', title="Proposals vs Consensus",
                          height=380, legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"))
        return _style_axes(fig)

    @staticmethod
    def decision_heatmap(allocation_history: list, zone_names: list) -> go.Figure:
        if not allocation_history:
            return go.Figure()
        steps = [h.get("step", i) for i, h in enumerate(allocation_history)]
        matrix = [[h.get("allocations", {}).get(n, 0) for h in allocation_history] for n in zone_names]
        fig = go.Figure(go.Heatmap(
            z=matrix, x=[f"S{s}" for s in steps], y=zone_names,
            colorscale=[[0, _BG], [0.5, _WARN], [1, _DANGER]],
            text=[[f"{v:.0f}" for v in row] for row in matrix], texttemplate="%{text}",
            hovertemplate="Zone: %{y}<br>Step: %{x}<br>Alloc: %{z:.1f}<extra></extra>"
        ))
        fig.update_layout(**_LAYOUT, title="Allocation Heatmap", height=340)
        return _style_axes(fig)

    @staticmethod
    def criteria_weight_evolution(weight_history: list) -> go.Figure:
        if not weight_history:
            return go.Figure()
        steps = list(range(len(weight_history)))
        traces = [
            ("Speed", [w.get("speed", 0) for w in weight_history], _DANGER),
            ("Fairness", [w.get("fairness", 0) for w in weight_history], _ACCENT),
            ("Cost", [w.get("cost", 0) for w in weight_history], _WARN),
            ("Resilience", [w.get("resilience", 0) for w in weight_history], _BLUE),
        ]
        fig = go.Figure()
        for name, vals, color in traces:
            # Convert hex color to rgba for fillcolor
            r_val = int(color[1:3], 16)
            g_val = int(color[3:5], 16)
            b_val = int(color[5:7], 16)
            fig.add_trace(go.Scatter(
                x=steps, y=vals, name=name, stackgroup='one',
                line=dict(color=color, width=1), fillcolor=f"rgba({r_val},{g_val},{b_val},0.25)"
            ))
        fig.update_layout(**_LAYOUT, title="AI Weight Evolution",
                          xaxis_title="Step", yaxis_title="Weight", height=340,
                          legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"))
        return _style_axes(fig)
